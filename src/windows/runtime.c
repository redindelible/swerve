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
};


struct ObjectHeader {
    uint64_t size;
    struct ObjectHeader* prev;
    void (*trace)(struct GCState*, void*);
};


struct Frame {
    uint64_t count;
    struct Frame* prev;
    struct ObjectHeader** objects[];
};


void* SWERVE_gc_allocate(struct GCState* gc_state, uint64_t size, void (*trace)(struct GCState*, void*)) {
    WaitForSingleObject(gc_state->gc_lock, INFINITE);
    struct ObjectHeader* obj = gc_state->from_space + gc_state->used_mem;
    gc_state->used_mem += size;
    obj->size = size;
    obj->trace = trace;
    ReleaseMutex(gc_state->gc_lock);
    return (void*) obj;
}


void SWERVE_gc_move(struct GCState* gc_state, struct ObjectHeader** obj_loc) {
    if (obj_loc == NULL) {
        return;
    }
    struct ObjectHeader* obj = *obj_loc;
    if (obj == NULL) {
        return;
    }
    if ((void*) gc_state->from_space <= obj && obj < (void*) gc_state->from_space + gc_state->space_size) {
        if (obj->size == 0) {
            *obj_loc = obj->prev;
            return;
        }
        uint64_t obj_size = obj->size;
        struct ObjectHeader* new_obj = gc_state->to_space + gc_state->to_used;
        gc_state->to_used += obj_size;

        memcpy(new_obj, obj, obj_size);
        new_obj->prev = gc_state->recent;
        gc_state->recent = new_obj;

        obj->size = 0;
        obj->prev = new_obj;

        *obj_loc = new_obj;
    }
}


void SWERVE_gc_check(struct Frame* frame, struct GCState* gc_state) {
    if (gc_state->plz_stop) {
        WaitForSingleObject(gc_state->gc_lock, INFINITE);

        while (frame != NULL) {
            for (uint64_t i = 0; i < frame->count; i++) {
                SWERVE_gc_move(gc_state, frame->objects[i]);
            }
            frame = frame->prev;
        }

        ReleaseMutex(gc_state->gc_lock);
        __atomic_add_fetch(&gc_state->num_completed, 1, __ATOMIC_SEQ_CST);
        WaitForSingleObject(gc_state->gc_release, INFINITE);
        __atomic_sub_fetch(&gc_state->num_completed, 1, __ATOMIC_SEQ_CST);
    }
}


struct ThreadStartInfo {
    struct GCState* gc_state;
    uint64_t (*f)(void*, void*);
    void* closure;
};


void SWERVE_begin_thread_helper(void* info_mem) {
    struct ThreadStartInfo info = *((struct ThreadStartInfo*) info_mem);
    free(info_mem);
    struct Frame init_frame = { 0, NULL, {}};
    info.f(&init_frame, info.closure);
    __atomic_sub_fetch(&info.gc_state->num_threads, 1, __ATOMIC_SEQ_CST);
}


void SWERVE_new_thread(struct GCState* gc_state, uint64_t (*f)(void*, void*), void* closure) {
    struct ThreadStartInfo* info = malloc(sizeof(struct ThreadStartInfo));
    info->gc_state = gc_state;
    info->f = f;
    info->closure = closure;
    __atomic_add_fetch(&info->gc_state->num_threads, 1, __ATOMIC_SEQ_CST);
    _beginthread(&SWERVE_begin_thread_helper, 0, info);
}


void SWERVE_gc_main(struct GCState* gc_state) {
    int i = 0;
    while (true) {
        SwitchToThread();
        if (gc_state->num_threads == 0) {
            return;
        }

        if (true) {
            gc_state->recent = NULL;
            gc_state->to_used = 0;

            ResetEvent(gc_state->gc_release);

            gc_state->plz_stop = true;

            while (true) {
                SwitchToThread();
                if (gc_state->num_threads == gc_state->num_completed) {
                    break;
                }
            }

            while (gc_state->recent != NULL) {
                struct ObjectHeader* recent = gc_state->recent;
                gc_state->recent = recent->prev;

                recent->trace(gc_state, recent);
            }

            // TODO just swap
            free(gc_state->from_space);
            gc_state->from_space = gc_state->to_space;
            gc_state->to_space = malloc(1024);
            memset(gc_state->to_space, 34, 1024);

//            printf("Completed collection: freed %lli bytes of memory.\n",  gc_state->used_mem - gc_state->to_used);

            gc_state->used_mem = gc_state->to_used;

            gc_state->plz_stop = false;
            SetEvent(gc_state->gc_release);
            while (true) {
                SwitchToThread();
                if (gc_state->num_completed == 0) {
                    break;
                }
            }
        }
    }
}


void SWERVE_gc_init(struct GCState* gc_state) {
    gc_state->gc_lock = CreateMutex(NULL, false, NULL);
    gc_state->gc_release = CreateEvent(NULL, true, true, NULL);
    gc_state->plz_stop = false;
    gc_state->num_threads = 0;
    gc_state->num_completed = 0;

    gc_state->space_size = 1024;
    gc_state->from_space = malloc(1024);
    gc_state->to_space = malloc(1024);

    gc_state->used_mem = 0;
    gc_state->to_used = 0;

    gc_state->recent = NULL;
}