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

    void* from_space;
    uint64_t from_size;
    void* to_space;
    uint64_t to_size;

    uint64_t used_mem;

    struct ObjectHeader* white;
    struct ObjectHeader* gray;
    struct ObjectHeader* black;
};


struct ObjectHeader {
    struct ObjectHeader* next;
    uint8_t color;
    void (*trace)(struct GCState*, void*);
};


struct Frame {
    uint64_t count;
    struct Frame* prev;
    void** objects[];
};


void* SWERVE_gc_allocate(struct GCState* gc_state, uint64_t size, void (*trace)(struct GCState*, void*)) {
    WaitForSingleObject(gc_state->gc_lock, INFINITE);
    struct ObjectHeader* obj = gc_state->from_space + gc_state->used_mem;
    gc_state->used_mem += size;
    obj->next = gc_state->gray;
    gc_state->gray = obj;
    obj->color = 1;
    obj->trace = trace;
    ReleaseMutex(gc_state->gc_lock);
    return (void*) obj;
}


void SWERVE_gc_check(struct Frame* frame, struct GCState* gc_state) {
    if (gc_state->plz_stop) {
        WaitForSingleObject(gc_state->gc_lock, INFINITE);



        ReleaseMutex(gc_state->gc_lock);
        __atomic_add_fetch(&gc_state->num_completed, 1, __ATOMIC_SEQ_CST);
        WaitForSingleObject(gc_state->gc_release, INFINITE);
    }
}


void* SWERVE_gc_move(struct GCState* gc_state, struct ObjectHeader* obj) {
    return obj;
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
    while (true) {
        SwitchToThread();
        if (gc_state->num_threads == 0) {
            return;
        }
        ResetEvent(gc_state->gc_release);
        gc_state->plz_stop = true;
        while (true) {
            SwitchToThread();
            if (gc_state->num_threads == gc_state->num_completed) {
                break;
            }
        }
        gc_state->num_completed = 0;
        gc_state->plz_stop = false;
        SetEvent(gc_state->gc_release);
    }
}


void SWERVE_gc_init(struct GCState* gc_state) {
    gc_state->gc_lock = CreateMutex(NULL, false, NULL);
    gc_state->gc_release = CreateEvent(NULL, true, true, NULL);
    gc_state->plz_stop = false;
    gc_state->num_threads = 0;
    gc_state->num_completed = 0;

    gc_state->from_space = malloc(1024);
    gc_state->from_size = 1024;
    gc_state->to_space = malloc(1024);
    gc_state->to_size = 1024;

    gc_state->used_mem = 0;

    gc_state->white = NULL;
    gc_state->gray = NULL;
    gc_state->black = NULL;
}