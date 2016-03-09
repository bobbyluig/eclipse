#ifndef _GIL_HPP_
#define _GIL_HPP_

#include <Python.h>

class releaseGIL {
public:
	inline releaseGIL() {
		save_state = PyEval_SaveThread();
	}

	inline ~releaseGIL() {
		PyEval_RestoreThread(save_state);
	}
private:
	PyThreadState *save_state;
};

#endif