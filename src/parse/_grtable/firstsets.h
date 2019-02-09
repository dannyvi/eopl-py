//
// Created by DannyV on 2018-12-11;
//

#ifndef COMPOST_FIRSTSETS_H
#define COMPOST_FIRSTSETS_H


#ifdef __cplusplus
extern "C" {
#endif

#include "symbol.h"

#define FWIDTH 128

typedef sym_ent_t firsts_t[FWIDTH];
extern firsts_t * NTFirst;

void init_first_sets(void);
void allocate_first_sets_space(void);
void free_first_sets_space(void) ;

sym_ent_list_t  * get_first_sets(sym_ent_t sym);

#ifdef __cplusplus
}
#endif

#endif
