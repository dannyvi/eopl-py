//
// Created by DannyV on 2018-12-1.
//

#include <stdlib.h>
#include "Python.h"

#include "symbol.h"
#include "grammar.h"
#include "firstsets.h"
#include "closure.h"


pitem_t build_pitem(prod_t *prod, sym_ent_t pos, sym_ent_t follow) {
    pitem_t p ;
    p.pnum = prod->pnum;
    p.dot = pos;
    p.follow = follow;
    return p;
}

int item_in_closure(pitem_t item, pitem_list_t * l){
    while (l->next) {
        if (item.pnum==l->item.pnum) {return 1;}
        l = l->next;
    }
    return 0;
}

void add_itm(pitem_t itm, pitem_list_t **clp) {
    (*clp)->item = itm;
    (*clp)->next = PyMem_Calloc(1, sizeof(pitem_list_t));
    (*clp) = (*clp)->next;
}

int cmpfunc (const void * a, const void * b) {
   return  ((pitem_t*)a)->pnum > ((pitem_t*)b)->pnum ? 1 : -1;
}

nterm_follow_t new_nterm_follow(sym_ent_t nterm, sym_ent_t follow) {
    nterm_follow_t c_ent;
    c_ent.nterm = nterm;
    c_ent.follow = follow;
    return c_ent;
}

static int entry_in_nflist(sym_ent_t nterm, sym_ent_t follow, nf_list_t  *c){
    while (c) {
        if (c->pair.nterm.index == nterm.index &&
            c->pair.follow.index== follow.index){ return 1; }
        c = c->next;
    };
    return 0;
}

void nflist_add(sym_ent_t nterm, sym_ent_t follow, nf_list_t * s){
    nterm_follow_t pair = new_nterm_follow(nterm, follow) ;
    while (s->next) {
        s = s->next;
    }
    s->pair = pair;
    s->next = PyMem_Calloc(1, sizeof(sym_ent_list_t ));
}

void free_nflist(nf_list_t *nf){
    nf_list_t *tmp;
    while((tmp=nf)!=NULL){
        nf = nf->next;
        PyMem_Free(tmp);
    }
}

static closure_t * build_closure(pitem_list_t *set,
                                 int label, int length,
                                 sym_ent_list_t *accept_symbols) {
    closure_t *t = PyMem_Calloc(1, sizeof(closure_t));
    t->label = label;
    t->length = length;
    t->items = PyMem_Calloc(length, sizeof(pitem_t));
    pitem_t *pp = t->items;
    while (set->next) {
        *pp = set->item;
        pp += 1;
        set = set->next;
    }
    mergesort(t->items, length, sizeof(pitem_t), cmpfunc);
    t->accept_symbols = accept_symbols;
    return t;
}

void free_closure_elems(closure_t * clos){
    PyMem_Free(clos->items);
    sym_ent_list_t * tmp, *acc=clos->accept_symbols;
    while((tmp=acc)!=NULL){
        acc = acc->next;
        PyMem_Free(tmp);
    }
    goto_list_t * tmpg, *golist = clos->goto_list;
    while((tmpg=golist)!=NULL){
        golist = golist->next;
        PyMem_Free(tmpg);
    }
}

closure_t * get_closure(pitem_list_t * queue, int label) {
    pitem_list_t  *qtail, *qiter;
    sym_ent_list_t *accept_symbols = new_sym_ent_list();
    nf_list_t *added = PyMem_Calloc(1, sizeof(nf_list_t));
    qtail = queue;
    int length = 0;
    while (qtail->next) {
        qtail = qtail->next;
        length += 1;
    }

    qiter = queue;
    while (qiter->next) {
        pitem_t item = qiter->item;
        sym_ent_t sym =item.body[(int)item.dot.index+1];
        //add accept input symbols.
        if (!entry_in_sym_ent_list(sym, accept_symbols)){
            sym_ent_list_add(sym, accept_symbols);
        }
        //add productions.
        if (sym.index && sym.type==NTERM) {
            sym_ent_t suffix = item.body[item.dot.index + 2].index ?
                               item.body[item.dot.index + 2] : item.follow;
            sym_ent_list_t  *terminals = get_first_sets(suffix);
            sym_ent_list_t  *itert = terminals;
            sym_ent_t posit;
            posit.index = 0;
            while (itert->next) {
                if (!entry_in_nflist(sym, itert->entry, added)){
                    nflist_add(sym, itert->entry, added);
                    pitem_list_t *prods = get_productions(&sym);
                    pitem_list_t *iterp = prods;
                    while(iterp->next) {
                        pitem_t newitem = build_pitem(&(iterp->item),
                                                      posit, itert->entry);
                        add_itm(newitem, &qtail);
                        length += 1;
                        iterp = iterp->next;
                    }
                    // PyMem_Free productions chain;
                    free_pitem_list(prods);
                    prods=iterp=NULL;
                }
                itert = itert->next;
            }
            free_sym_ent_list(terminals);
            terminals=itert=NULL;
        }
        qiter = qiter->next;
    }

    closure_t *t = build_closure(queue, label, length, accept_symbols);
    free_pitem_list(queue);
    queue=qtail=qiter=NULL;
    free_nflist(added);
    added = NULL;
    return t;
}

