#include <stdint.h>
#include <stdlib.h>


struct GCState {
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
    struct ObjectHeader* obj = (struct ObjectHeader*) malloc(size);
    obj->next = gc_state->gray;
    gc_state->gray = obj;
    obj->color = 1;
    obj->tag = tag;
    return (void*) obj;
}