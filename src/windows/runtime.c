#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <windows.h>
#include <process.h>


struct GCState {
    HANDLE gc_lock;
    HANDLE gc_release;
    bool plz_stop;
    uint64_t num_threads;
    uint64_t num_completed;

    struct ObjectHeader* recent;

    void* from_space;
    void* to_space;
    uint64_t space_size;

    uint64_t used_mem;
    uint64_t to_used;

    bool in_trace;
};


struct GCState gc_state;


struct ObjectHeader {
    uint64_t size;
    struct ObjectHeader* prev;
    void (*trace)(void*);
};


struct Frame {
    uint64_t count;
    uint64_t line;
    struct Frame* prev;
    struct ObjectHeader* held;
    struct ObjectHeader** objects[];
};


void* SWERVE_gc_allocate(uint64_t size, void (*trace)(void*)) {
    WaitForSingleObject(gc_state.gc_lock, INFINITE);
    struct ObjectHeader* obj;
    obj = gc_state.from_space + gc_state.used_mem;
    gc_state.used_mem += size;
    memset(obj, 0, size);
    obj->size = size;
    obj->prev = NULL;
    obj->trace = trace;
    ReleaseMutex(gc_state.gc_lock);
    return (void*) obj;
}


struct ObjectHeader* SWERVE_gc_move(struct ObjectHeader* obj) {
    if (obj == NULL) {
        return NULL;
    }
    if ((void*) gc_state.from_space <= obj && obj < (void*) gc_state.from_space + gc_state.space_size) {
        uint64_t obj_size = obj->size;
        if (obj_size == 0) {
            return obj->prev;
        }
        struct ObjectHeader* new_obj = gc_state.to_space + gc_state.to_used;
        gc_state.to_used += obj_size;

        memcpy(new_obj, obj, obj_size);
        new_obj->prev = gc_state.recent;
        gc_state.recent = new_obj;

        obj->size = 0;
        obj->prev = new_obj;
        return new_obj;
    } else if ((void*) gc_state.to_space <= obj && obj < (void*) gc_state.to_space + gc_state.space_size) {
        printf("we REALLY shouldn't be here, %p\n", obj);
        return obj;
    } else {
        return obj;
    }
}

struct ObjectHeader* SWERVE_gc_trace_helper(void* frame, void* closure, struct ObjectHeader* obj) {
    struct ObjectHeader* new_obj = SWERVE_gc_move(obj);
    return new_obj;
}


struct ObjectHeader* SWERVE_gc_check(struct Frame* frame, struct ObjectHeader* obj) {
    if (gc_state.in_trace) {
        return obj;
    }
    if (gc_state.plz_stop) {
        WaitForSingleObject(gc_state.gc_lock, INFINITE);

        gc_state.in_trace = true;
        obj = SWERVE_gc_move(obj);

        while (frame != NULL) {
            frame->held = SWERVE_gc_move(frame->held);
            for (uint64_t i = 0; i < frame->count; i++) {
                struct ObjectHeader** loc = frame->objects[i];
                if (loc != NULL) {
                    *loc = SWERVE_gc_move(*loc);
                }
            }
            frame = frame->prev;
        }
        gc_state.in_trace = false;

        ReleaseMutex(gc_state.gc_lock);
        __atomic_add_fetch(&gc_state.num_completed, 1, __ATOMIC_SEQ_CST);
        WaitForSingleObject(gc_state.gc_release, INFINITE);
        __atomic_sub_fetch(&gc_state.num_completed, 1, __ATOMIC_SEQ_CST);
    }
    return obj;
}


struct ThreadStartInfo {
    uint64_t (*f)(void*, void*);
    void* closure;
};


void SWERVE_begin_thread_helper(void* info_mem) {
    struct ThreadStartInfo info = *((struct ThreadStartInfo*) info_mem);
    free(info_mem);
    struct Frame init_frame = { 0, 0, NULL, NULL, {} };
    info.f(&init_frame, info.closure);
    __atomic_sub_fetch(&gc_state.num_threads, 1, __ATOMIC_SEQ_CST);
}


void SWERVE_new_thread(uint64_t (*f)(void*, void*), void* closure) {
    struct ThreadStartInfo* info = malloc(sizeof(struct ThreadStartInfo));
    info->f = f;
    info->closure = closure;
    __atomic_add_fetch(&gc_state.num_threads, 1, __ATOMIC_SEQ_CST);
    _beginthread(&SWERVE_begin_thread_helper, 0, info);
}


void SWERVE_gc_main() {
    int i = 0;
    while (true) {
        SwitchToThread();
        if (gc_state.num_threads == 0) {
            return;
        }

        if (true) {
            gc_state.recent = NULL;
            gc_state.to_used = 0;

            ResetEvent(gc_state.gc_release);

            gc_state.plz_stop = true;

            while (true) {
                SwitchToThread();
                if (gc_state.num_threads == gc_state.num_completed) {
                    break;
                }
            }

            gc_state.in_trace = true;
            while (gc_state.recent != NULL) {
                struct ObjectHeader* recent = gc_state.recent;
                gc_state.recent = recent->prev;

                recent->trace(recent);
            }
            gc_state.in_trace = false;

            // TODO just swap
            free(gc_state.from_space);
            gc_state.from_space = gc_state.to_space;
            gc_state.to_space = malloc(1024);
            memset(gc_state.to_space, 34, 1024);

//            printf("Completed collection: freed %lli bytes of memory.\n",  gc_state.used_mem - gc_state.to_used);

            gc_state.used_mem = gc_state.to_used;

            gc_state.plz_stop = false;
            SetEvent(gc_state.gc_release);
            while (true) {
                SwitchToThread();
                if (gc_state.num_completed == 0) {
                    break;
                }
            }
        }
    }
}


void SWERVE_gc_init() {
    gc_state.gc_lock = CreateMutex(NULL, false, NULL);
    gc_state.gc_release = CreateEvent(NULL, true, true, NULL);
    gc_state.plz_stop = false;
    gc_state.num_threads = 0;
    gc_state.num_completed = 0;

    gc_state.space_size = 1024;
    gc_state.from_space = malloc(1024);
    gc_state.to_space = malloc(1024);

    gc_state.used_mem = 0;
    gc_state.to_used = 0;

    gc_state.recent = NULL;

    gc_state.in_trace = false;
}


void SWERVE_display(char* s) {
    printf("%s\n", s);
}

void SWERVE_display_pointer(char* s, void* p) {
    printf("%s %p\n", s, p);
}