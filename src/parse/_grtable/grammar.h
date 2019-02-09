//
// Created by DannyV on 2018-12-10;
//

#ifndef COMPOST_GRAMMAR_H
#define COMPOST_GRAMMAR_H


#ifdef __cplusplus
extern "C" {
#endif

#include <stdlib.h>

#include "symbol.h"

typedef union prod_t {
    __uint128_t pnum;
    struct {
        sym_ent_t body[14];
        sym_ent_t dot;
        sym_ent_t follow;
    } ;
} prod_t, pitem_t;

typedef struct pitem_list_t pitem_list_t;
struct pitem_list_t {
    pitem_t item;
    pitem_list_t *next;
};

extern prod_t *GramTable;
extern size_t GramCount;

void allocate_gram_space(size_t num);
void free_gram_space(void);

pitem_list_t * get_productions(sym_ent_t *sym);
void free_pitem_list(pitem_list_t * items);

#ifdef __cplusplus
}
#endif

#endif
