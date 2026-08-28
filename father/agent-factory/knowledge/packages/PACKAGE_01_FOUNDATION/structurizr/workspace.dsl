workspace "FATHER Knowledge Factory" "C4 model for Package 01" {

    model {
        analyst = person "Analyst" "Investigates, validates evidence and requests recommendations."

        father = softwareSystem "FATHER Knowledge Factory" "Evidence-backed knowledge factory and research graph." {
            frontend = container "Frontend" "Analyst workspace, graph and evidence UI." "Next.js / React"
            backend = container "Backend API" "Projects, sessions, access and API facade." "FastAPI"
            ai = container "AI / Evidence Service" "RAG, evidence retrieval, prompts, model calls and citation validation." "Python" {
                controller = component "Recommendation Controller" "Coordinates /get_recommendation."
                policy = component "Policy Guard" "Validates scope, role and request policy."
                rag = component "RAG Manager" "Retrieval and context assembly."
                evidence = component "Evidence Retriever" "Resolves exact fragments, locators, hashes and versions."
                prompts = component "Prompt Template Factory" "Builds versioned evidence-first prompts."
                llmClient = component "LLM Client" "Adapter for local or approved external models."
                citation = component "Citation Validator" "Checks claims against evidence."
                projector = component "Knowledge Projector" "Applies role projection without cloning canonical nodes."
                audit = component "Audit Emitter" "Emits trace spans and outcomes."
            }
            vector = container "Vector DB" "Semantic retrieval index." "pgvector / Qdrant"
            sql = container "SQL DB" "Canonical documents, fragments, nodes, edges, reviews and traces." "SQLite M1 -> PostgreSQL"
            original = container "Original Store" "Immutable originals and source revisions." "Local FS / S3-compatible"
            review = container "Review / Promotion Service" "Review lifecycle and KB_READY gate." "Python"
            trace = container "Trace / Audit Store" "trace_id/span_id/entity links and debug events." "JSONL + SQL"
        }

        llm = softwareSystem "LLM Endpoint" "Local or approved external inference endpoint."

        analyst -> father.frontend "Uses" "HTTPS"
        father.frontend -> father.backend "REST/JSON"
        father.backend -> father.ai "POST /get_recommendation" "HTTPS/JSON"
        father.ai -> father.vector "Semantic search"
        father.ai -> father.sql "Canonical read/write"
        father.ai -> father.original "Resolve source evidence"
        father.ai -> llm "Inference"
        father.review -> father.sql "Review/promotion state"
        father.ai -> father.trace "Trace events"
        father.backend -> father.trace "Trace events"

        father.ai.controller -> father.ai.policy "Validate request"
        father.ai.controller -> father.ai.rag "Retrieve context"
        father.ai.rag -> father.ai.evidence "Resolve exact evidence"
        father.ai.rag -> father.ai.prompts "Build prompt"
        father.ai.rag -> father.ai.llmClient "Generate candidate"
        father.ai.controller -> father.ai.citation "Validate claims"
        father.ai.controller -> father.ai.projector "Apply role view"
        father.ai.controller -> father.ai.audit "Emit audit"
        father.ai.evidence -> father.vector "Search candidates"
        father.ai.evidence -> father.sql "Resolve canonical fragments"
        father.ai.evidence -> father.original "Resolve original source"
        father.ai.llmClient -> llm "Chat completion"
        father.ai.audit -> father.trace "Write span/event"
    }

    views {
        systemContext father "C1" {
            include *
            autoLayout lr
        }

        container father "C2" {
            include *
            autoLayout lr
        }

        component father.ai "C3-AI" {
            include *
            autoLayout lr
        }

        styles {
            element "Person" {
                shape person
            }
            element "Container" {
                shape roundedbox
            }
            element "Component" {
                shape component
            }
            element "Software System" {
                shape roundedbox
            }
        }
    }
}
