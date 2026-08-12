#include <stdexcept>


enum class Status { draft, approved, published, archived };

struct Document {
    Status status{Status::draft};
};

class invalid_transition : public std::logic_error {
public:
    using std::logic_error::logic_error;
};

bool allowed(Status from, Status to) {
    switch (from) {
        case Status::draft:
            return to == Status::approved;
        case Status::approved:
            return to == Status::draft || to == Status::published;
        case Status::published:
            return to == Status::archived;
        case Status::archived:
            return false;
    }
    return false;
}

Document transition(Document doc, Status target) {
    if (!allowed(doc.status, target)) {
        throw invalid_transition("invalid document transition");
    }
    doc.status = target;
    return doc;
}
