#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <windows.h>


struct GCState {
    HANDLE gc_lock;
    void* white;
    void* gray;
    void* black;
};


struct ObjectHeader {
    struct ObjectHeader* next;
    uint8_t color;
    void* tag;
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


void SWERVE_gc_init(struct GCState* gc_state) {
    gc_state->gc_lock = CreateMutex(NULL, false, NULL);
    gc_state->white = NULL;
    gc_state->gray = NULL;
    gc_state->black = NULL;
}