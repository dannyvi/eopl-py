//
//Created by DannyV on 2018-12-10.
//

#include "Python.h"
#include "grammar.h"
#include "firstsets.h"

firsts_t * NTFirst;

void allocate_first_sets_space(void){
    NTFirst = (firsts_t *) PyMem_Calloc(NTSIZE, sizeof(firsts_t));
}

void free_first_sets_space(void) {
    PyMem_Free(NTFirst);
    NTFirst = NULL;
}

static int entry_in_list(sym_ent_t ent, firsts_t list){
    int counter = 0;
    while(list[counter].index || counter==0){
        if (list[counter].index == ent.index) {return 1;}
        counter += 1;
    }
    return 0;
}

static void get_entry_headers(sym_ent_t entry, sym_ent_t * firsts) {
    int counter = 0;
    for (size_t i=0;i<GramCount;i++){
        if (GramTable[i].body[0].index == entry.index) {
            sym_ent_t sym = GramTable[i].body[1];
            if (!entry_in_list(sym, firsts)){
                firsts[counter] = sym;
                counter += 1;
            }
        }
    }
}


static void process_first_set(sym_ent_t * term_set, sym_ent_t entry) {
    //two first sets list, an nterm list to parse, and the target to fill.
    firsts_t queue={{0}};
    int qtail = 0, qiter = 0, tmpos = 0;

    //init queue
    queue[qtail] = entry;
    sym_ent_t current = queue[qtail];
    qtail += 1;
    while (current.index!=0 || qiter==0) {
        if (current.type!=NTERM) {
            if (!entry_in_list(current, term_set)) {
                term_set[tmpos]=current;
                tmpos += 1;
            }
        }
        else {
            firsts_t headers = {{0}};
            int headpos = 0;
            get_entry_headers(current, (sym_ent_t *)(&headers));
            while(headers[headpos].index) {
                if (!entry_in_list(headers[headpos], queue)){
                    queue[qtail] = headers[headpos];
                    qtail += 1;
                }
                headpos += 1;
            }
        }
        qiter += 1;
        current = queue[qiter];
    }
}

void init_first_sets(void) {
    sym_ent_t entry;
    firsts_t * flist;
    for (int i=0;i<NTSIZE;i++) {
        if (SymEntPosit[i].index || i==0) {             // has an NTerm Entry
            entry.index = i;
            flist = NTFirst+i;
            process_first_set((sym_ent_t *)flist, entry);
        }
    }
}

sym_ent_list_t  * get_first_sets(sym_ent_t sym){
    if (sym.type != NTERM){
        sym_ent_list_t  * s = sym_ent_list_create(&sym, 1);
        return s;
    }
    else {
        int entry = (int) sym.index;
        int counter = 0;
        sym_ent_list_t  *set = PyMem_Calloc(1,sizeof(sym_ent_list_t ));
        sym_ent_list_t  *sp = set;
        while (NTFirst[entry][counter].index){
            sp->entry = NTFirst[entry][counter];
            sp->next = PyMem_Calloc(1, sizeof(sym_ent_list_t ));
            sp = sp->next;
            counter += 1;
        }
        return set;
    }
}
