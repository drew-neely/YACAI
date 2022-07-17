#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <experimental/coroutine>
#include <exception>
#include <iostream>
#include <vector>

using namespace std;
using namespace experimental;

/*
	This file contains a Generator class implementing coroutines in a 
	way suitable for use with chess move generation. The Generator class
	is also iterable, allowing for use with enhanced for loops. Each 
	Generator object may only be iterated once - the coroutine does not
	automatically reset.
	C++ coroutines are only available in C++20 and are currently experimental,
	so IDEs may not understand the imports/semantics.
*/
template<typename T>
class Generator {

	struct Promise {
		T value_;
		exception_ptr exception_;
		bool finished_;

		Promise() : finished_(false) {}

		Generator get_return_object() {
			return Generator(handle_type::from_promise(*this));
		}
		suspend_always initial_suspend() { return {}; }
		suspend_always final_suspend() noexcept { return {}; }
		void unhandled_exception() { 
			exception_ = current_exception(); // Saving exception
		}
		suspend_always yield_value(T value) {
			value_ = value; // Saving value
			return {};
		}
		void return_void() {
			finished_ = true; // Mark the coroutine as having completed
		}
	};

	struct EndIterator {};
	
public:

	using value_type = T;
	using promise_type = Promise;
	using handle_type = coroutine_handle<Promise>;
 
	Generator(handle_type h) : handle_(h) {}
	~Generator() { handle_.destroy(); }

	/*
		This function is called when the generator oobject is called
		This resumes execution of the coroutine and returns the value 
		which is co_yielded
	*/
	T operator()() {
		handle_();
		if (handle_.promise().exception_) { 
			rethrow_exception(handle_.promise().exception_); // deliver coroutine exception in called context
		}
		return handle_.promise().value_;
	}

	/*
		Iterator support for the generator object so it may be used 
		in an enhanced for loop
	*/
	class Iterator {
	public:

		using iterator_category = std::input_iterator_tag;
		using difference_type   = std::ptrdiff_t;
		using value_type        = T;

		Iterator(Generator& generator) : generator(&generator) {}

		value_type operator*() const { 
			return generator->handle_.promise().value_;
		}

		value_type operator->() const { 
			return generator->handle_.promise().value_;
		}

		Iterator& operator++() {
			generator->handle_.resume();
			return *this;
		}

		Iterator& operator++(int) {
			generator->handle_.resume();
			return *this;
		}

		bool operator== (const EndIterator&) const {
			return generator->handle_.promise().finished_;
		}
	
	private:
		Generator* generator;
	};

	Iterator begin() {
		Iterator it(*this);
		return ++it;
	}

	EndIterator end() {
		return end_sentinel;
	}

private:
	handle_type handle_;
	EndIterator end_sentinel;

public:
	///////////////
	//// helper functions for easier use of generator object
	///////////////

	/*
		Returns if the generator object has returned it's last value
		Will do undefined behavior if generator object is called while 
		it is finished
	*/
	bool finished() {
		return handle_.promise().finished_;
	}

	/*
		Constructs a vector containing all the values that would be generated.
		Using this method defats the purpose of using a coroutine instead of a
		function returning a vector, so only use in non-performance critical 
		regions (eg. test bench checking)
		Consumes output - Generator cannot be re-used
	*/
	vector<T> to_vector() {
		vector<T> vec;
		for(T t : *this) {
			vec.push_back(t);
		}
		return vec;
	}

	/*
		Used for situations where all that matters is the size of the generator ouput
		Consumes output - Generator cannot be re-used after this is called
	*/
	int size() {
		int size = 0;
		for(T t : *this) {
			size++;
		}
		return size;
	}

	/*
		Used for situations where all that matters is if there is at least 1 element
		in the generator output.
		If false is returned, generator was run until first value was produced
		If true is returned, generator ran to completion
		Consumes output - Generator cannot be re-used after this is called
	*/
	int is_empty() {
		(*this)();
		return finished();
	}


};