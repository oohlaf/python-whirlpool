/**
 * This is just a wrapper to the Whirlpool hashing function.
 * The Whirlpool reference implementations are public domain,
 * as is this code.
 *
 * Wrapper written by James Cleveland with help from #python
 * on irc.freenode.net
 */

#define PY_SSIZE_T_CLEAN 1
#include <Python.h>
#include "Whirlpool.c"
static PyObject *
whirlpool_hash(PyObject *self, PyObject *args) {
    struct NESSIEstruct w;
    unsigned char digest[DIGESTBYTES];
    Py_ssize_t data_size;
    unsigned char *data;


    if(!PyArg_ParseTuple(args, "s#", &data, &data_size))
        return NULL;
    
    NESSIEinit(&w);
    NESSIEadd(data, data_size*8, &w);
    NESSIEfinalize(&w, digest);

    return Py_BuildValue("s#", digest, DIGESTBYTES);
}

PyMethodDef methods[] = {
    {"hash", whirlpool_hash, METH_VARARGS,
        "Hash with whirlpool algorithm."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initwhirlpool() {
    (void) Py_InitModule("whirlpool", methods);
}
