//
// Created by DannyV on 2018-12-8.
//

#include <Python.h>

#include "symbol.h"


sym_str_t * SymTable;
sym_ent_t * SymIndex;
sym_ent_t * SymEntPosit;
int SymCount;

void allocate_symbol_space(void){
    SymTable = (sym_str_t *) PyMem_Calloc(TBLEN, sizeof(sym_str_t));
    SymIndex = (sym_ent_t *) PyMem_Calloc(TBLEN, sizeof(sym_ent_t));
    SymEntPosit = (sym_ent_t *) PyMem_Calloc(TBLEN, sizeof(sym_ent_t));
    SymCount = 0;
}

void free_symbol_space(void){
    PyMem_Free(SymTable);
    PyMem_Free(SymIndex);
    PyMem_Free(SymEntPosit);
    SymTable = NULL;
    SymIndex = NULL;
    SymEntPosit = NULL;
    SymCount = 0;
}

sym_ent_t get_sym_ent(sym_ent_t startp, char * str){
    int len = startp.type==NTERM ? 128 : 64;
    char * table_str;
    sym_ent_t result={.index=255};
    for (int i=startp.index; i<startp.index+len; i++){
        table_str = SymTable[i];
        if (strcmp(str, table_str)==0) {
            result.index = i;
            return result;
        }
    }
    return result;
}


void sym_ent_list_add(sym_ent_t sym, sym_ent_list_t * sets){
    sym_ent_list_t  *s = sets;

        while (s->next) {
            s = s->next;
        }
        s->entry = sym;
        s->next = PyMem_Calloc(1, sizeof(sym_ent_list_t ));
}

sym_ent_list_t  * new_sym_ent_list(void) {
    sym_ent_list_t  *ss = PyMem_Calloc(1, sizeof(sym_ent_list_t ));
    return ss;
}

sym_ent_list_t  * sym_ent_list_create(sym_ent_t syms[], size_t size){
    sym_ent_list_t  *ss = PyMem_Calloc(1, sizeof(sym_ent_list_t ));
    sym_ent_list_t  *kk = ss;
    for (size_t i=0; i<size; i++){
        ss->entry = syms[i];
        ss->next = PyMem_Calloc(1, sizeof(sym_ent_list_t ));
        ss = ss->next;
    }
    return kk;
}

int entry_in_sym_ent_list(sym_ent_t sym, sym_ent_list_t  *c){
    while (c){
        if (c->entry.index == sym.index){ return 1; }
        c = c->next;
    };
    return 0;
}

void free_sym_ent_list(sym_ent_list_t * elist) {
    sym_ent_list_t * tmp;
    while((tmp=elist)!=NULL){
        elist = elist->next;
        PyMem_Free(tmp);
    }
}
