#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <windows.h>


struct GCState {
    HANDLE gc_lock;
    bool plz_stop;
    struct ObjectHeader* white;
    struct ObjectHeader* gray;
    struct ObjectHeader* black;
};


struct ObjectHeader {
    struct ObjectHeader* next;
    uint8_t color;
    void* tag;
};


struct Frame {
    uint64_t count;
    struct Frame* prev;
    void* closure;
    void** objects[];
};


void* SWERVE_gc_allocate(struct GCState* gc_state, uint64_t size, void* tag) {
    WaitForSingleObject(gc_state->gc_lock, INFINITE);
    struct ObjectHeader* obj = (struct ObjectHeader*) malloc(size);
    obj->next = gc_state->gray;
    gc_state->gray = obj;
    obj->color = 1;
    obj->tag = tag;
    ReleaseMutex(gc_state->gc_lock);
    return (void*) obj;
}


void SWERVE_gc_check(struct Frame* frame, struct GCState* gc_state) {
    if (gc_state->plz_stop) {
        WaitForSingleObject(gc_state->gc_lock, INFINITE);
        ReleaseMutex(gc_state->gc_lock);
    }
//    while (frame) {
//        printf("count: %i\n", frame->count);
//        frame = frame->prev;
//    }
//    printf("done trace\n");
}


void SWERVE_gc_init(struct GCState* gc_state) {
    gc_state->gc_lock = CreateMutex(NULL, false, NULL);
    gc_state->plz_stop = false;
    gc_state->white = NULL;
    gc_state->gray = NULL;
    gc_state->black = NULL;
}