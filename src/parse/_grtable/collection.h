//
//Created by DannyV on 2018-12-10.
//

#ifndef COMPOST_COLLECTION_H
#define COMPOST_COLLECTION_H


#ifdef __cplusplus
extern "C" {
#endif

#include "closure.h"

typedef struct clos_list_t clos_list_t;

struct clos_list_t {
    closure_t c;
    clos_list_t *next;
};

clos_list_t * closure_collection(void);
void free_closure_collection(clos_list_t * coln);
void free_goto_list(goto_list_t *lst);

#ifdef __cplusplus
}
#endif

#endif
