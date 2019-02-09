//
//Created by DannyV on 2018-12-10.
//

#ifndef COMPOST_STATEMAP_H
#define COMPOST_STATEMAP_H


#ifdef __cplusplus
extern "C" {
#endif

#include "collection.h"

typedef char* action_t ;

PyObject * get_states_list(clos_list_t *c, Py_ssize_t length);


#ifdef __cplusplus
}
#endif

#endif
