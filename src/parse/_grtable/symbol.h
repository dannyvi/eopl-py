//
//Created by DannyV on 2018-12-8.
//


#ifndef COMPOST_SYMBOL_H
#define COMPOST_SYMBOL_H

#ifdef __cplusplus
extern "C" {
#endif


#define TBLEN 256
#define NTERM 0
#define TERM 2
#define VALUE 3
#define NTSIZE 128

typedef char sym_str_t[64];
typedef union sym_ent_t {
    unsigned char index;
    struct {
        unsigned char num:6;            // the index in the symbol_table.
        unsigned char type:2;           // symbol_t 0 is NTERM 2: TERM, 3:VALUE.
    };
} sym_ent_t;

typedef struct sym_ent_list_t  sym_ent_list_t ;
struct sym_ent_list_t  {
    sym_ent_t entry;
    sym_ent_list_t  *next;
};

// 256 symbol string table store in heap space, allocated in init function.

extern sym_str_t * SymTable;
extern sym_ent_t * SymIndex;            // the symbol position in SymTable.
extern sym_ent_t * SymEntPosit;         // symbol entry position in SymIndex.
extern int SymCount;                    // how many symbols in the grammar.


void allocate_symbol_space(void);
void free_symbol_space(void);
sym_ent_t get_sym_ent(sym_ent_t startp, char * str);

void sym_ent_list_add(sym_ent_t sym, sym_ent_list_t * sets);
sym_ent_list_t  * new_sym_ent_list(void);
sym_ent_list_t  * sym_ent_list_create(sym_ent_t syms[], size_t size);
int entry_in_sym_ent_list(sym_ent_t sym, sym_ent_list_t  *c);
void free_sym_ent_list(sym_ent_list_t * elist) ;

#ifdef __cplusplus
}
#endif

#endif
