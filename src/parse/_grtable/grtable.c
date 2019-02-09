/*
 * Created by DannyV on 2018-12-8.
 */

#include <Python.h>

#include "symbol.h"
#include "grammar.h"
#include "closure.h"
#include "firstsets.h"
#include "collection.h"
#include "statemap.h"

/*   should be called by grtable.gen_syntax_table(NT, T, V, grm, symbols)
 *   return the syntax table.
 */

//-------------------------------symbols----------------------------------------

PyObject *classNT, *classT, *classV;

static sym_ent_t get_symbol_start_point(PyObject *instance){
    //NTERM starts from 0, TERM starts from 128, VALUE starts from 192;
    sym_ent_t startp={0};
    if ( PyObject_IsInstance(instance, classNT)){
        startp.type = NTERM;
    } else if ( PyObject_IsInstance(instance, classT)){
        startp.type = TERM;
    } else if ( PyObject_IsInstance(instance, classV)){
        startp.type = VALUE;
    }
    return startp;
}

static void init_symbols(PyObject* symbols){
    PyObject *sym, *attr_sym;
    const char *sym_str = " ";
    Py_ssize_t length = PyList_Size(symbols);
    Py_ssize_t size;

    for (Py_ssize_t i=0; i<length; i++){
        sym = PyList_GetItem(symbols, i);
        sym_ent_t startp = get_symbol_start_point(sym);
        attr_sym = PyObject_GetAttrString(sym, "symbol");
        sym_str = PyUnicode_AsUTF8AndSize(attr_sym, &size);
        while(SymTable[startp.index][0]){ startp.index += 1 ;}
        strcpy(SymTable[startp.index], sym_str);
        SymIndex[SymCount] = startp;
        sym_ent_t pos = {.index=SymCount};
        SymEntPosit[startp.index] = pos;
        SymCount += 1;
    }
}

// ------------------------------grammar----------------------------------------

prod_t build_production(PyObject *prod ){
    PyObject * sym, *attr_sym;
    sym_ent_t startp, entry;
    Py_ssize_t size;
    const char *sym_str = " ";
    prod_t product={0};
    long length = PyList_Size(prod);
    for (int i = 0; i < length; i++) {
        sym = PyList_GetItem(prod, i);
        startp = get_symbol_start_point(sym);
        attr_sym = PyObject_GetAttrString(sym, "symbol");
        sym_str = PyUnicode_AsUTF8AndSize(attr_sym, &size);
        entry = get_sym_ent(startp, (char *)sym_str);
        product.body[i] = entry;
    }
    return product;
}

static void init_grammar(PyObject* grammar){
    PyObject *prod;
    Py_ssize_t length = PyList_Size(grammar);
    prod_t product;

    // initialize the grammar space;
    allocate_gram_space(length);

    for (Py_ssize_t i=0; i<length; i++){
        prod = PyList_GetItem(grammar, i);
        product = build_production(prod);
        GramTable[i] = product;
    }
}

//---------------------------------API------------------------------------------

PyObject* grtable_gen_syntax_table(PyObject* self, PyObject* args) {
    PyObject *NT, *T, *V, *symbols, *grammar;
    if (!PyArg_ParseTuple(args, "OOOOO", &NT, &T, &V, &symbols, &grammar)) {
        PyErr_Print();
        return NULL;
    }

    // initialize class type.
    classNT = NT;
    classT = T;
    classV = V;


    allocate_symbol_space();

    init_symbols(symbols);

    // allocate_gram_space in init_grammar func for convinience of length arg.
    init_grammar(grammar);

    allocate_first_sets_space();
    init_first_sets();

    clos_list_t * coln = closure_collection();
    int length = 0;
    clos_list_t * l = coln;
    while(l->next){
        l = l->next;
        length += 1;
    }
    PyObject *  result = get_states_list(coln, length);
    free_closure_collection(coln);

    free_first_sets_space();
    free_gram_space();
    free_symbol_space();

    return result;

}


static char grtable_gen_syntax_table_docs[] = "generate syntax table.\n";


static PyMethodDef module_methods[] = {
        {"gen_syntax_table", (PyCFunction)grtable_gen_syntax_table, METH_VARARGS, grtable_gen_syntax_table_docs},
        {NULL, NULL, 0, NULL}
};


static struct PyModuleDef grtable = {
                PyModuleDef_HEAD_INIT,
                "grtable", /* name of module */
                "usage: grtable.init_symbols(type,type,type,symbols)\n", /* module documentation, may be NULL */
                -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
                module_methods
};

PyMODINIT_FUNC PyInit_grtable(void)
{
    return PyModule_Create(&grtable);
}
