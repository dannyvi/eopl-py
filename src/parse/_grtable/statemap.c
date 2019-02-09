//
// Created by DannyV on 2018-12-10;
//

#include <stdlib.h>
#include "Python.h"

#include "statemap.h"
#include "collection.h"


static int get_prod_number(pitem_t *item){
    prod_t p = *item;
    p.dot.index = 0;
    p.follow.index=0;
    for (size_t i=0; i<GramCount; i++) {
        if (p.pnum==GramTable[i].pnum){return (int)i;}
    }
    //never reach here;
    return -1;
}

static void write_list_line(closure_t *clos, PyObject *list) {
    action_t action = (action_t) PyMem_Calloc(8, sizeof(char));
    int golabel, strlen;
    // shift actions
    goto_list_t *golist = clos->goto_list;
    if (golist) {
        while (golist->next){
            sym_ent_t posit = golist->by_sym_ent;
            golabel = golist->closure.label;
            strlen = snprintf( NULL, 0, "%d", golabel );
            posit.type==NTERM ? snprintf( action, strlen + 1, "%d", golabel ) :
                                snprintf( action, strlen + 2, "s%d", golabel );
            PyObject * listitem = Py_BuildValue("s", action);
            PyList_SetItem(list, SymEntPosit[posit.index].index, listitem);
            golist = golist->next;
        }
    }
    // check reduce action in closure items;
    sym_ent_t startp={.type=VALUE};
    sym_ent_t accept_entry = get_sym_ent(startp, "$");
    pitem_t acc_item = {.body={{0},{1}}, .dot={1}, .follow=accept_entry};
    pitem_t *pitem = clos->items;
    for (int i=0; i<clos->length; i++,pitem++){
        if (acc_item.pnum == pitem->pnum){
            snprintf(action, 2, "%s", "$");
            PyObject * listitem = Py_BuildValue("s", action);
            PyList_SetItem(list, SymEntPosit[accept_entry.index].index, listitem);
        }
        else{
            int plen = 0;
            while(pitem->body[plen].index || plen==0){
                plen += 1;
            }
            if (pitem->dot.index == plen-1) {
                int number = get_prod_number(pitem);
                strlen = snprintf( NULL, 0, "%d", number );
                snprintf(action, strlen+2, "r%d", number);
                PyObject * listitem = Py_BuildValue("s", action);
                PyList_SetItem(list, SymEntPosit[pitem->follow.index].index, listitem);
            }
        }
    }
    PyMem_Free(action);
    action = NULL;
}


PyObject * get_states_list(clos_list_t *c, Py_ssize_t length) {
    PyObject * result;
    int sym_size = SymCount;

    // pass 1, default error "." chars for every action ;
    action_t action = ".";
    result = PyList_New(length);
    for (Py_ssize_t i=0; i<length; i++) {
        PyObject * line = PyList_New(sym_size);
        for (Py_ssize_t j=0; j<sym_size; j++){
            PyObject * elem = Py_BuildValue("s", action);
            PyList_SetItem(line, j, elem);
        }
        PyList_SetItem(result, i, line);
    }
    // pass 2, fill lines in closures of col_chain.
    while (c->next) {
        closure_t *clos = &(c->c);
        PyObject *item = PyList_GetItem(result, clos->label);
        write_list_line(clos, item);
        c=c->next;
    }


    return result;
}

