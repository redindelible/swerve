#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <windows.h>
#include <process.h>


struct AllocBlock {
    struct AllocBlock* next_block;
    uint32_t item_size;  // in regular blocks (size <= 256), this can be treated as a uint16_t
    uint32_t free_map;   // in non-regular blocks, this doesn't matter
    uint8_t mem[];
};


struct GCState {
    HANDLE gc_lock;
    HANDLE gc_release;
    bool plz_stop;
    bool in_trace;
    uint64_t num_threads;
    uint64_t num_completed;

    bool white_is_1;
    struct ObjectHeader* white;
    struct ObjectHeader* gray;
    struct ObjectHeader* black;

    // blocks[n] contains blocks with item size 32 * (n + 1) bytes
    // blocks[0] contains blocks with item size 32 bytes
    // blocks[7] contains blocks with item size 256 bytes

    struct AllocBlock* blocks[7];
} gc_state;


void SWERVE_gc_init() {
    gc_state.gc_lock = CreateMutex(NULL, false, NULL);
    gc_state.gc_release = CreateEvent(NULL, true, true, NULL);
    gc_state.plz_stop = false;
    gc_state.in_trace = false;
    gc_state.num_threads = 0;
    gc_state.num_completed = 0;

    gc_state.white_is_1 = true;
    gc_state.white = NULL;
    gc_state.gray = NULL;
    gc_state.black = NULL;

    for (int i = 0; i < 7; i++) {
        gc_state.blocks[i] = NULL;
    }
}


struct ObjectHeader {
    struct AllocBlock* block;
    struct ObjectHeader* prev;
    void (*trace)(void*);
};


struct Frame {
    uint64_t count;
    uint64_t line;
    struct Frame* prev;
    struct ObjectHeader* closure;
    struct ObjectHeader** objects[];
};


struct AllocBlock* SWERVE_gc_add_block(uint32_t item_size) {
    if (item_size == 0) {
        exit(-1);
    }
    if (item_size <= 256) {
        struct AllocBlock* block = malloc(sizeof(struct AllocBlock) + (item_size * 16));
        block->next_block = NULL;
        block->item_size = item_size;
        block->free_map = (1 << 16) - 1;
        return block;
    } else {
        struct AllocBlock* block = malloc(sizeof(struct AllocBlock) + item_size);
        block->next_block = NULL;
        block->item_size = item_size;
        block->free_map = 1;
        return block;
    }
}


#define MARK_BLACK(obj) do { uint64_t* prev_ptr = (uint64_t*) &(obj)->prev; if (gc_state.white_is_1) *prev_ptr = *prev_ptr & ~((uint64_t) 1); else *prev_ptr = *prev_ptr | ((uint64_t) 1); } while (0)
#define MARK_WHITE(obj) do { uint64_t* prev_ptr = (uint64_t*) &(obj)->prev; if (!gc_state.white_is_1) *prev_ptr = *prev_ptr & ~((uint64_t) 1); else *prev_ptr = *prev_ptr | ((uint64_t) 1); } while (0)
#define IS_BLACK(obj) ((((uint64_t) (obj)->prev) & ((uint64_t) 1)) == (gc_state.white_is_1 ? 0 : 1))
#define IS_WHITE(obj) ((((uint64_t) (obj)->prev) & ((uint64_t) 1)) == (gc_state.white_is_1 ? 1 : 0))
#define PREV_PTR(obj) ((struct ObjectHeader*) (((uint64_t) (obj)->prev) & ~((uint64_t) 1)))


void* SWERVE_gc_allocate(uint64_t size, void (*trace)(void*)) {
    WaitForSingleObject(gc_state.gc_lock, INFINITE);

    struct ObjectHeader* obj;
    struct AllocBlock* block;

    if (size <= 256) {
        int index = size / 32 - (size % 32 ? 0 : 1);
        block = gc_state.blocks[index];
        while (block != NULL && block->free_map == 0) {
            block = block->next_block;
        }
        if (block == NULL) {
            block = SWERVE_gc_add_block((index + 1) * 32);
            block->next_block = gc_state.blocks[index];
            gc_state.blocks[index] = block;
        }
        uint32_t free_index = __builtin_ctz(block->free_map);
        obj = (struct ObjectHeader*) &block->mem[free_index * block->item_size];
        block->free_map &= ~(((uint32_t) 1) << free_index);
    } else {
        block = SWERVE_gc_add_block(size);
        obj = (struct ObjectHeader*) &block->mem[0];
        block->free_map &= ~((uint32_t) 1);
    }

    memset(obj, 0, size);
    obj->block = block;
//    printf("Obj block: %p\n", obj->block);
    obj->prev = gc_state.gray;
    gc_state.gray = obj;
    MARK_BLACK(obj);
    obj->trace = trace;
    ReleaseMutex(gc_state.gc_lock);
    return (void*) obj;
}


void SWERVE_gc_mark(struct ObjectHeader* obj) {
    if (obj == NULL) {
        return;
    }

    if (IS_WHITE(obj)) {
        obj->prev = gc_state.gray;
        gc_state.gray = obj;
        MARK_BLACK(obj);
    }
}

void SWERVE_gc_trace_helper(void* frame, void* closure, struct ObjectHeader* obj) {
    SWERVE_gc_mark(obj);
}


void SWERVE_gc_check(struct Frame* frame, struct ObjectHeader* obj) {
    if (gc_state.in_trace) {
        return;
    }
    if (gc_state.plz_stop) {
        WaitForSingleObject(gc_state.gc_lock, INFINITE);

        SWERVE_gc_mark(obj);

        while (frame != NULL) {
            SWERVE_gc_mark(frame->closure);
            for (uint64_t i = 0; i < frame->count; i++) {
                struct ObjectHeader** loc = frame->objects[i];
                if (loc != NULL) {
                    SWERVE_gc_mark(*loc);
                }
            }
            frame = frame->prev;
        }

        ReleaseMutex(gc_state.gc_lock);
        __atomic_add_fetch(&gc_state.num_completed, 1, __ATOMIC_SEQ_CST);
        WaitForSingleObject(gc_state.gc_release, INFINITE);
        __atomic_sub_fetch(&gc_state.num_completed, 1, __ATOMIC_SEQ_CST);
    }
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
            gc_state.gray = NULL;

            ResetEvent(gc_state.gc_release);

            gc_state.plz_stop = true;

            while (true) {
                SwitchToThread();
                if (gc_state.num_threads == gc_state.num_completed) {
                    break;
                }
            }

            gc_state.in_trace = true;
            while (gc_state.gray != NULL) {
                struct ObjectHeader* next_gray = gc_state.gray;
                gc_state.gray = PREV_PTR(next_gray);

                next_gray->trace(next_gray);

                next_gray->prev = gc_state.black;
                gc_state.black = next_gray;
                MARK_BLACK(next_gray);
            }

            struct ObjectHeader* garbage = gc_state.white;
            while (garbage != NULL) {
                struct AllocBlock* block = garbage->block;
                int index = ((intptr_t) garbage - (intptr_t) block) / block->item_size;
                block->free_map &= ~(((uint64_t) 1) << index);
                garbage = PREV_PTR(garbage);
            }

            gc_state.white = gc_state.black;
            gc_state.black = NULL;
            gc_state.white_is_1 = !gc_state.white_is_1;

            gc_state.in_trace = false;
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


void SWERVE_display(char* s) {
    printf("%s\n", s);
}

void SWERVE_display_pointer(char* s, void* p) {
    printf("%s %p\n", s, p);
}