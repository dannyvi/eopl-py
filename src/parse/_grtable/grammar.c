//
// Created by DannyV on 2018-12-10;
//

#include <stdlib.h>
#include "Python.h"

#include "grammar.h"


prod_t *GramTable;
size_t GramCount;

void allocate_gram_space(size_t num){
    GramTable = (prod_t *) PyMem_Calloc(num, sizeof(prod_t));
    GramCount = num;
}

void free_gram_space(void){
    PyMem_Free(GramTable);
    GramTable = NULL;
    GramCount = 0;
}

pitem_list_t * get_productions(sym_ent_t *sym){
    if (sym->type!=NTERM){return NULL;}
    pitem_list_t *pl = PyMem_Calloc(1, sizeof(pitem_list_t));
    pitem_list_t *result = pl;
    for (size_t i=0;i<GramCount;i++) {
        if (GramTable[i].body[0].index==sym->index) {
            pl->item = GramTable[i];
            pl->next = PyMem_Calloc(1, sizeof(pitem_list_t));
            pl = pl->next;
        }
    }
    return result;
}

void free_pitem_list(pitem_list_t * items){
    pitem_list_t * tmp;
    while ((tmp=items)!=NULL){
        items = items->next;
        PyMem_Free(tmp);
    }
}
