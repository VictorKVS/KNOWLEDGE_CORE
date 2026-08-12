#include <deque>
#include <stdexcept>
#include <string>

class queue_full : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}

    void put(std::string item) {
        if (items_.size() >= capacity_) {
            throw queue_full("queue capacity reached");
        }
        items_.push_back(std::move(item));
    }

    std::string get() {
        auto item = std::move(items_.front());
        items_.pop_front();
        return item;
    }

    std::size_t size() const { return items_.size(); }

private:
    std::size_t capacity_;
    std::deque<std::string> items_;
};
