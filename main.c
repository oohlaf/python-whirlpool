/**
 * This is just a wrapper to the Whirlpool hashing function.
 * The Whirlpool reference implementations are public domain,
 * as is this code.
 *
 * Wrapper written by James Cleveland with help from #python
 * on irc.freenode.net
 */

#include <Python.h>
#include "Whirlpool.c"

typedef struct {
    PyObject_HEAD
    NESSIEstruct whirlpool; /* the context holder */
} whirlpoolobject;

static PyTypeObject Whirlpooltype;

#define is_whirlpoolobject(v) ((v)->ob_type == &Whirlpooltype)

static whirlpoolobject *
newwhirlpoolobject(void)
{
    whirlpoolobject *wpp;

    wpp = PyObject_New(whirlpoolobject, &Whirlpooltype);
    if (wpp == NULL)
        return NULL;

    NESSIEinit(&wpp->whirlpool); /* actual initialisation */
    return wpp;
}

/* Whirlpool methods */

static void
whirlpool_dealloc(whirlpoolobject *wpp)
{
    PyObject_Del(wpp);
}

/* Whirlpool methods-as-attributes */

static PyObject *
whirlpool_update(whirlpoolobject *self, PyObject *args)
{
    Py_buffer view;

    if (!PyArg_ParseTuple(args, "s*:update", &view))
        return NULL;

    NESSIEadd((unsigned char*)view.buf,
              Py_SAFE_DOWNCAST(view.len, Py_ssize_t, unsigned int) * 8,
              &self->whirlpool);

    PyBuffer_Release(&view);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(update_doc,
"update (arg)\n\
\n\
Update the whirlpool object with the string arg. Repeated calls are\n\
equivalent to a single call with the concatenation of all the\n\
arguments.");


static PyObject *
whirlpool_digest(whirlpoolobject *self)
{
    NESSIEstruct wpContext;
    unsigned char digest[DIGESTBYTES];

    /* Make a temporary copy, and perform the final */
    wpContext = self->whirlpool;
    NESSIEfinalize(&wpContext, digest);

    return PyString_FromStringAndSize((const char *)digest, sizeof(digest));
}

PyDoc_STRVAR(digest_doc,
"digest() -> string\n\
\n\
Return the digest of the strings passed to the update() method so\n\
far. This is a binary string which may contain non-ASCII characters,\n\
including null bytes.");


static PyObject *
whirlpool_hexdigest(whirlpoolobject *self)
{
    NESSIEstruct wpContext;
    PyObject *retval;
    unsigned char digest[DIGESTBYTES];
    char *hexdigest;
    int i, j;

    /* Get the raw (binary) digest value */
    wpContext = self->whirlpool;
    NESSIEfinalize(&wpContext, digest);

    /* Create a new string */
    retval = PyString_FromStringAndSize(NULL, sizeof(digest) * 2);
    if (!retval)
        return NULL;
    hexdigest = PyString_AsString(retval);
    if (!hexdigest) {
        Py_DECREF(retval);
        return NULL;
    }

    /* Make hex version of the digest */
    for(i=j=0; i<sizeof(digest); i++) {
        char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c>9) ? c+'a'-10 : c+'0';
        hexdigest[j++] = c;
        c = (digest[i] & 0xf);
        c = (c>9) ? c+'a'-10 : c+'0';
        hexdigest[j++] = c;
    }
    return retval;
}

PyDoc_STRVAR(hexdigest_doc,
"hexdigest() -> string\n\
\n\
Like digest(), but returns the digest as a string of hexadecimal digits.");


static PyObject *
whirlpool_copy(whirlpoolobject *self)
{
    whirlpoolobject *wpp;

    if ((wpp = newwhirlpoolobject()) == NULL)
        return NULL;

    wpp->whirlpool = self->whirlpool;
    return (PyObject *)wpp;
}

PyDoc_STRVAR(copy_doc,
"copy() -> whirlpool object\n\
\n\
Return a copy (``clone'') of the whirlpool object.");


PyMethodDef whirlpool_methods[] = {
    {"update",    (PyCFunction)whirlpool_update,    METH_VARARGS, update_doc},
    {"digest",    (PyCFunction)whirlpool_digest,    METH_NOARGS,  digest_doc},
    {"hexdigest", (PyCFunction)whirlpool_hexdigest, METH_NOARGS,  hexdigest_doc},
    {"copy",      (PyCFunction)whirlpool_copy,      METH_NOARGS,  copy_doc},
    {NULL, NULL} /* sentinel */
};


static PyObject *
whirlpool_get_block_size(PyObject *self, void *closure)
{
    return PyInt_FromLong(WBLOCKBYTES);
}

static PyObject *
whirlpool_get_digest_size(PyObject *self, void *closure)
{
    return PyInt_FromLong(DIGESTBYTES);
}

static PyObject *
whirlpool_get_name(PyObject *self, void *closure)
{
    return PyString_FromStringAndSize("WHIRLPOOL", 9);
}

static PyGetSetDef whirlpool_getseters[] = {
    {"digest_size",
     (getter)whirlpool_get_digest_size, NULL,
     NULL,
     NULL},
    {"block_size",
     (getter)whirlpool_get_block_size, NULL,
     NULL,
     NULL},
    {"name",
     (getter)whirlpool_get_name, NULL,
     NULL,
     NULL},
    {NULL} /* sentinel */
};


PyDoc_STRVAR(module_doc,
"This module implements the interface to the whirlpool message digest\n\
algorithm. It operates on messages less than 2^256 bits in length,\n\
and produces a message digest of 512 bits. Its use is quite straighforward:\n\
use new() to create a whirlpool object. You can now feed this object with\n\
arbitrary strings using the update() method. At any point you can ask it for\n\
the digest of the concatenation of the strings fed to it so far.\n\
\n\
Functions:\n\
new([arg]) -- return a new whirlpool object, initialized with arg if provided\n\
hash(arg) -- DEPRECATED, returns a whirlpool digest of arg, for backward \
compatibility\n\
\n\
Special Objects:\n\
\n\
WhirlpoolType -- type object for whirlpool objects");

PyDoc_STRVAR(whirlpooltype_doc,
"A whirlpool represents the object used to calculate the WHIRLPOOL checksum of\n\
a string of information.\n\
\n\
Methods:\n\
\n\
update(arg) -- updates the current digest with an additional string\n\
digest() -- return the current digest value\n\
hexdigest() -- return the current digest as a string of hexadecimal digits\n\
copy() -- return a copy of the current whirlpool object");

static PyTypeObject Whirlpooltype = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "whirlpool.whirlpool",         /*tp_name*/
    sizeof(whirlpoolobject),       /*tp_size*/
    0,                             /*tp_itemsize*/
    /* methods */
    (destructor)whirlpool_dealloc, /*tp_dealloc*/
    0,                             /*tp_print*/
    0,                             /*tp_getattr*/
    0,                             /*tp_setattr*/
    0,                             /*tp_compare*/
    0,                             /*tp_repr*/
    0,                             /*tp_as_number*/
    0,                             /*tp_as_sequence*/
    0,                             /*tp_as_mapping*/
    0,                             /*tp_hash*/
    0,                             /*tp_call*/
    0,                             /*tp_str*/
    0,                             /*tp_getattro*/
    0,                             /*tp_setattro*/
    0,                             /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,            /*tp_flags*/
    whirlpooltype_doc,             /*tp_doc*/
    0,                             /*tp_traverse*/
    0,                             /*tp_clear*/
    0,                             /*tp_richcompare*/
    0,                             /*tp_weaklistoffset*/
    0,                             /*tp_iter*/
    0,                             /*tp_iternext*/
    whirlpool_methods,             /*tp_methods */
    0,                             /*tp_members */
    whirlpool_getseters,           /*tp_getset */
};


/* Whirlpool functions */

static PyObject *
whirlpool_new(PyObject *self, PyObject *args)
{
    whirlpoolobject *wpp;
    Py_buffer view = { 0 };

    if (!PyArg_ParseTuple(args, "|s*:new", &view))
        return NULL;

    if ((wpp = newwhirlpoolobject()) == NULL) {
        PyBuffer_Release(&view);
        return NULL;
    }

    if (view.len > 0) {
        NESSIEadd((unsigned char*)view.buf,
                  Py_SAFE_DOWNCAST(view.len, Py_ssize_t, unsigned int) * 8,
                  &wpp->whirlpool);
    }
    PyBuffer_Release(&view);

    return (PyObject *)wpp;
}

PyDoc_STRVAR(new_doc,
"new([arg]) -> whirlpool object\n\
\n\
Return a new whirlpool object. If arg is present, the method call update(arg)\n\
is made.");


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

PyDoc_STRVAR(hash_doc,
"Returns a hash of argument using the whirlpool algorithm.\n\
This function is deprecated. Please use new() and hexdigest().");


/* List of functions exported by this module */

static PyMethodDef whirlpool_functions[] = {
    {"new",  (PyCFunction)whirlpool_new,  METH_VARARGS, new_doc},
    {"hash", (PyCFunction)whirlpool_hash, METH_VARARGS, hash_doc},
    {NULL, NULL} /* sentinel */
};


/* Initialize this module */

PyMODINIT_FUNC
initwhirlpool(void)
{
    PyObject *m, *d;

    Py_TYPE(&Whirlpooltype) = &PyType_Type;
    if (PyType_Ready(&Whirlpooltype) < 0)
        return;
    m = Py_InitModule3("whirlpool", whirlpool_functions, module_doc);
    if (m == NULL)
        return;
    PyModule_AddIntConstant(m, "digest_size", DIGESTBYTES);
    PyModule_AddIntConstant(m, "block_size", WBLOCKBYTES);
    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "WhirlpoolType", (PyObject *)&Whirlpooltype);
}

