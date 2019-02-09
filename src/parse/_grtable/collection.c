#include "Python.h"

#include "closure.h"
#include "collection.h"

static int eq_closure_t(closure_t *a, closure_t *b) {
    if (a->length != b->length) {return 0;}
    pitem_t *ai = a->items, *bi = b->items;
    for (int i=0;i<a->length; i++, ai++, bi++) {
        if (ai->pnum!=bi->pnum) {return 0;}
    }
    return 1;
}

static closure_t * ret_closure_in_collection(closure_t *clos, clos_list_t *cc){
    while(cc->next){
        if (eq_closure_t(clos, &cc->c)){return &cc->c;}
        cc = cc->next;
    }
    return NULL;
}

static closure_t * goto_closure(closure_t *clos, sym_ent_t sentry) {
    pitem_list_t *ss = PyMem_Calloc(1, sizeof(pitem_list_t));
    pitem_list_t *set = ss;
    pitem_t *ptm = clos->items;
    for (int i=0; i<clos->length; i++,ptm++) {
        int pos = (int)(ptm->dot.index);
        if(ptm->body[pos+1].index==sentry.index && sentry.index!=0){
            sym_ent_t ent = {.index=pos+1};
            pitem_t newitem = build_pitem(ptm, ent, ptm->follow);
            add_itm(newitem, &set);
        }
    }
    return ss->next ? get_closure(ss, NONE_LABEL) : NULL ;
}

static void add_clos(closure_t *t, clos_list_t **coll){
    (*coll)->c = *t;
    (*coll)->next = PyMem_Calloc(1, sizeof(clos_list_t));
    (*coll) = (*coll)->next;
}

static int has_in_goto_list(closure_t *clos, closure_t *goclos, sym_ent_t *ent){
    if (!clos->goto_list) {return 0;}
    goto_list_t *g = clos->goto_list;
    while (g->next) {
        if (g->by_sym_ent.index==ent->index &&
            eq_closure_t(&g->closure, goclos)) {return 1;}
        g = g->next;
    }
    return 0;
}

static void add_goto_list(closure_t *clos, closure_t goclos, sym_ent_t * ent){
    //not initialized condition
    if (!clos->goto_list) {
        goto_list_t *g = PyMem_Calloc(1, sizeof(goto_list_t));
        g->by_sym_ent = *ent;
        g->closure = goclos;
        g->next = PyMem_Calloc(1, sizeof(goto_list_t));
        clos->goto_list = g;
        clos->goto_tail = g->next;
    }
    else {  // closure already has at least 1 goto target.
        if (!has_in_goto_list(clos, &goclos, ent)){
            goto_list_t *g = clos->goto_tail;
            g->by_sym_ent = *ent;
            g->closure = goclos;
            g->next = PyMem_Calloc(1, sizeof(goto_list_t));
            clos->goto_tail = g->next;
        }
    }
}

void free_goto_list(goto_list_t *lst){
    goto_list_t *xcg;
    while ((xcg=lst)!=NULL) {
        lst = lst->next;
        PyMem_Free(xcg);
    }
}

static pitem_t get_start_item(void) {
    sym_ent_t posit = {.index=0};
    sym_ent_t startp={.type=VALUE};
    sym_ent_t sentry = get_sym_ent(startp, "$");
    return build_pitem(&GramTable[0], posit, sentry);
}

clos_list_t * closure_collection(void) {
    int label = 0;
    clos_list_t * coll = PyMem_Calloc(1, sizeof(clos_list_t));
    clos_list_t *qp = coll, *countq = coll;

    pitem_t startitem = get_start_item();
    pitem_list_t *start = PyMem_Calloc(1, sizeof(pitem_list_t));
    start->item = startitem;
    start->next = PyMem_Calloc(1, sizeof(pitem_list_t));
    closure_t *t = get_closure(start, label);

    add_clos(t, &qp);

    while (countq->next){
        closure_t * clos = &(countq->c);
        sym_ent_list_t * ent = clos->accept_symbols;
        while(ent->next) {
            closure_t * goclos = goto_closure(clos, ent->entry);
            if (goclos) {
                closure_t * retclos = ret_closure_in_collection(goclos, coll);
                if (!retclos){
                    label += 1;
                    goclos->label=label;
                    add_clos(goclos, &qp);
                    add_goto_list(clos, *goclos, &ent->entry);
                }
                else {
                    add_goto_list(clos, *retclos, &ent->entry);
                    free_closure_elems(goclos);
                    PyMem_Free(goclos);
                    goclos=NULL;
                }
            }
            ent = ent->next;
        }
        countq = countq->next;
    }
    return coll;
}


void free_closure_collection(clos_list_t * coln) {
    clos_list_t * tmp;
    while ((tmp=coln)!=NULL){
        coln = coln->next;
        free_closure_elems(&tmp->c);
        PyMem_Free(tmp);
    }

}
