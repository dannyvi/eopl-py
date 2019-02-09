
#ifndef COMPOST_TEST_H
#define COMPOST_TEST_H

#ifdef __cplusplus
extern "C" {
#endif
#include "grammar.h"
#include <Python.h>
extern PyObject *classNT, *classT, *classV;

PyObject* grtable_gen_syntax_table(PyObject* self, PyObject* obj) ;

void display_item(prod_t prd, int prd_or_item, int ent_or_str);
#ifdef __cplusplus
}
#endif

#endif
