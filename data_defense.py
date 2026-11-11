MEMBERS_DATA = [
    {
        "name": "MEMBER 1: ABDULLAH (Roll No: BSDSF23A035)",
        "role": "Group Leader & System Architect / AI Brain Lead",
        "stat": "27 Tickets | 116 Story Points | Sprints 1 to 4 Done, Sprints 5 & 6 To Do",
        "simple_summary": "I am the builder of our custom AI Brain. Instead of paying OpenAI or calling standard ChatGPT APIs (which hallucinate and cost money), I coded a custom Causal Transformer Neural Network in PyTorch from scratch. It has 1.32 million parameters and reads car repair manuals to write verified diagnostic fixes. I also built the Consistent Hash Ring (160 Virtual Nodes) so incoming car data is distributed evenly across computers without crashing any single server.",
        "what_built_detail": [
            "Custom Subword BPE Tokenizer: Teaches the AI model how to read mechanical words in English, Urdu, and Roman Urdu (4,000 token vocabulary).",
            "4-Layer Causal Transformer Decoder: 1,321,728 parameters built in PyTorch with triangular causal self-attention masks so it predicts verified repair words step-by-step.",
            "Consistent Hash Ring (160 Virtual Nodes): Uses MurmurHash3 to spread vehicle data across storage nodes evenly, keeping data skew variance below 5%.",
            "FastAPI Gateway: High-speed asynchronous server connecting all 5 members' modules together."
        ],
        "scenarios": [
            (
                "Tough Question 1: 'Why did you build your own Transformer LM from scratch instead of just calling the OpenAI GPT-4 API with a prompt?'",
                "Sir, commercial LLMs like GPT-4 are a massive black box. In safety-critical automotive diagnostics, GPT-4 has three fatal flaws: First, it hallucinates ungrounded torque specs and wrong repair steps that can destroy an engine. Second, sending private vehicle telemetry to foreign commercial APIs violates data privacy and costs heavy dollars per token. Third, an academic FYP in Data Science requires proving we understand the deep mathematical architecture of attention matrices and next-token cross-entropy loss. We built our 1.32M parameter PyTorch Transformer to run completely offline on local hardware with zero cost, zero latency spikes, and 100% citation grounding to official OEM manuals."
            ),
            (
                "Tough Question 2: 'What is a Consistent Hash Ring, and why not just use normal modulo hashing (Hash(VIN) % N)?'",
                "Sir, normal modulo hashing is catastrophic in distributed systems. If we have 4 servers and one server dies (N becomes 3), almost 100% of the vehicle records get shuffled to different servers, causing a massive data migration storm that crashes the system. With our Consistent Hash Ring using 160 virtual nodes, when a server joins or leaves, only K/N keys (less than 25%) are re-routed. The virtual nodes ensure that no single server gets overloaded, keeping server load variance below 5%."
            ),
            (
                "Tough Question 3: 'What if a car owner asks about a Ferrari or an unsupported 1990 tractor?'",
                "Sir, generic AI would hallucinate a fake answer. Our system has a strict Selective Abstention Gate: If the retrieval similarity score is below 0.35, the system politely abstains and says: 'This vehicle is outside our verified 2015-2025 Pakistani fleet scope. Please consult an authorized specialist.' We prioritize user safety over answering blindly."
            )
        ]
    },
    {
        "name": "MEMBER 2: TALHA ALI BHATTI (Roll No: BSDSF23A016)",
        "role": "Lead Distributed Storage Warehouse & High-Speed Ingestion Engineer",
        "stat": "26 Tickets | 101 Story Points | Sprints 1 to 4 Done, Sprints 5 & 6 To Do",
        "simple_summary": "I build the ultra-fast data warehouse and the high-speed pipes. When thousands of cars send sensor signals every second (speed, engine heat, RPM), standard databases lock up and crash. I built an OBD-II CAN-Bus Telemetry Streamer capable of pumping 10,000 signals every second, set up our distributed MinIO S3 Object Storage cluster, and implemented Content-Addressable Storage (CAS) Deduplication that saves over 70% hard-drive space by never saving duplicate files twice.",
        "what_built_detail": [
            "MinIO S3 Distributed Object Storage Cluster: Private S3-compliant object storage with isolated buckets (raw-telemetry, processed-parquet, model-checkpoints).",
            "SHA-256 CAS Deduplication Engine: Splits files into cryptographic chunks, hashes them, and skips uploading identical files, saving 70%+ disk space.",
            "10,000 msg/s OBD-II CAN-Bus Telemetry Streamer: Multi-threaded synthetic generator simulating real Pakistani driving conditions.",
            "Snappy Parquet Columnar Lakehouse: Organizes vehicle records in columnar partitions (make/model/year/region) so analytical queries read only the needed columns."
        ],
        "scenarios": [
            (
                "Tough Question 1: 'What happens to your storage when 10,000 fleet vehicles send sensor data every second? Won't your disk run out of space?'",
                "Sir, that is the exact reason we implemented a Snappy Columnar Parquet Lakehouse instead of dumping raw JSON. Raw JSON takes 420 MB for our test fleet, but our Snappy-compressed Parquet files take only 88 MB—a massive 79% compression ratio! Furthermore, my CAS Deduplication engine uses SHA-256 hashes to ensure duplicate manuals, video frames, and repeated sensor baselines are stored exactly once, preventing disk exhaustion."
            ),
            (
                "Tough Question 2: 'Why did you use MinIO S3 instead of just saving files in a normal Windows folder or SQLite?'",
                "Sir, saving files in normal local folders lacks distributed replication, access policies, and scalability. SQLite locks the entire database file on concurrent writes, causing timeouts under heavy sensor streams. MinIO gives us enterprise-grade, S3-compatible distributed object storage right on our local hardware. It supports asynchronous multipart uploads, bucket lifecycle retention, and distributed fault tolerance without paying expensive Amazon AWS cloud bills."
            ),
            (
                "Tough Question 3: 'What is the \"Small File Problem\" in Big Data lakes, and how did you solve it?'",
                "Sir, when continuous streaming data arrives in micro-batches (e.g. 1-second chunks), it creates thousands of tiny 50 KB files. This chokes NameNodes and query engines. I built an automated Parquet Compaction Job (AUT-111) that runs in the background and consolidates 100 small files into optimized 128 MB analytical chunks, accelerating read speeds by 80%."
            )
        ]
    },
    {
        "name": "MEMBER 3: DANIAL HAMEED (Roll No: BSDSF23A014)",
        "role": "Lead Data Engineer, Multilingual Corpus & Bloom Filter Specialist",
        "stat": "27 Tickets | 112 Story Points | Sprints 1 to 4 Done, Sprints 5 & 6 To Do",
        "simple_summary": "I am the data collector, librarian, and language specialist. I curated and cleaned 111 automotive dataset files across 14 categories and extracted 326 clean chunks from 45 official service handbooks (Toyota Corolla, Honda Civic, Suzuki Swift) with exact page numbers. I also built the Urdu and Roman Urdu automotive dictionary so car owners can describe faults in local words (like 'dhuwan' or 'jhatka'), and built a Counting Bloom Filter that checks if an error code exists in less than 1 millisecond.",
        "what_built_detail": [
            "111-File Multi-Modal Automotive Dataset: Cleaned, deduplicated, and standardized datasets from PakWheels, mechanic interview videos, and Facebook QA.",
            "Structure-Aware 45 OEM Manuals Chunking: Extracted 326 structured chunks isolating warning boxes, torque specs, and repair steps with exact page numbers.",
            "Urdu & Roman Urdu Automotive Lexicon: Maps 150+ colloquial mechanic terms (e.g., 'dhuwan', 'garam', 'jhatka', 'missing') to formal SAE J2012 fault codes.",
            "Counting Bloom Filter: Memory-efficient probabilistic filter with k=4 hash functions guaranteeing zero false negatives and sub-millisecond lookups."
        ],
        "scenarios": [
            (
                "Tough Question 1: 'Pakistani car owners don't speak technical English. If a driver says \"Gari subah subah lambi self leti hai aur dhuwan marti hai\", how does your system understand it?'",
                "Sir, that was one of the core problems of our FYP! Standard Western tools fail here. I engineered a domain-specific Urdu and Roman Urdu Automotive Lexicon (AUT-136). It takes colloquial words like 'lambi self' and maps them to 'delayed crank / fuel pressure regulator fault', and maps 'dhuwan' to 'exhaust smoke emission'. It normalizes informal terminology into standard SAE J2012 diagnostic trouble codes before querying the manuals."
            ),
            (
                "Tough Question 2: 'What is a Bloom Filter, and why use it if you can just query the database with SELECT * FROM dtc WHERE code = X?'",
                "Sir, when 10,000 sensor events arrive every second, running 10,000 SQL disk queries per second for non-existent or rare trouble codes causes severe disk I/O bottleneck. My Counting Bloom Filter (AUT-106) sits in high-speed RAM. It uses double-hashing to check code membership in O(1) time (< 0.05ms). It mathematically guarantees ZERO false negatives. If the Bloom filter says NO, we instantly know the code does not exist without touching the disk, eliminating 90% of useless disk reads!"
            ),
            (
                "Tough Question 3: 'How did you ensure your dataset is not full of fake or biased internet comments?'",
                "Sir, I built a Canonical Cleaning & Quality Validator pipeline (AUT-145). It strips HTML tags, removes duplicate spam, and only extracts verified mechanical resolutions where authorized mechanics or workshop manuals verified the root cause. Furthermore, we tag every record with provenance metadata ('seeded', 'verified_mechanic', or 'oem_manual')."
            )
        ]
    },
    {
        "name": "MEMBER 4: AHMAD ZAHID (Roll No: BSDSF23A033)",
        "role": "Lead ML Triage Doctor, Safety Calibration & Workshop Fraud Inspector",
        "stat": "28 Tickets | 126 Story Points | Sprints 1 to 4 Done, Sprints 5 & 6 To Do",
        "simple_summary": "I am the safety doctor and fraud inspector. In car care, a machine learning mistake can cost a life: If the AI misdiagnoses a broken radio, it's fine, but if it misses brake failure or engine overheating, someone could crash. I built a Cost-Sensitive Triage Classifier with a 10x safety penalty on critical faults. I also implemented Platt Scaling Calibration so the AI never guesses, and built the NLI Workshop Invoice Verifier that checks mechanic quotes against official car manuals to catch overcharging.",
        "what_built_detail": [
            "Cost-Sensitive Triage Classifier: Multi-class ML model using an asymmetric 10x cost penalty matrix on critical safety faults, dropping the critical false negative rate to 11.4%.",
            "Platt Scaling & Temperature Calibration: Sigmoid regression aligning raw neural probabilities to true empirical risk, reducing Expected Calibration Error (ECE) below 0.05.",
            "NLI Workshop Invoice Verifier: Natural Language Inference engine cross-checking mechanic repair quotes against official OEM manuals to detect overcharging.",
            "Proposal Section 17 Ethical Standards: Enforces neutral, evidence-backed explanations that protect consumers without making slanderous legal claims against workshops."
        ],
        "scenarios": [
            (
                "Tough Question 1: 'Standard classifiers have high overall accuracy (95%). Why did you need a \"Cost-Sensitive\" classifier with a 10x penalty?'",
                "Sir, in safety engineering, standard accuracy is dangerously misleading! If a car has 95 minor cosmetic scratches and 5 fatal hydraulic brake failures, a naive model that predicts \"Minor\" every time gets 95% accuracy, but 5 drivers could die! In our Cost-Sensitive Triage model (AUT-107), missing a Critical safety fault is penalized 10 times more heavily than a false alarm. This reduced our Critical False Negative Rate from 68.2% down to 11.4% on held-out test folds, ensuring safety-critical faults are never overlooked."
            ),
            (
                "Tough Question 2: 'A mechanic tells a customer: \"Your Corolla needs a complete engine overhaul for Rs. 150,000\". How does your system prove the mechanic is cheating?'",
                "Sir, that is exactly why I built the NLI Repair Verifier (AUT-132). The user enters the mechanic's invoice line item. Our system retrieves the official Toyota Corolla service handbook section for the active symptoms. It runs Natural Language Inference (Premise Entailment) and reports: \"Unsupported. Official Toyota Manual Section 14-2 specifies that symptom P0300 on this vehicle requires cleaning the spark plug (Rs. 1,500) and inspecting the ignition coil, NOT a complete engine overhaul.\" It gives the driver verified proof right on their phone!"
            ),
            (
                "Tough Question 3: 'What is Platt Scaling, and why does your model need it?'",
                "Sir, deep neural networks are notoriously overconfident—they might say they are 99% confident when they are actually wrong! Platt Scaling fits a logistic regression sigmoid on model log-odds. If our calibrated confidence falls below 70%, the system triggers our Selective Abstention Gate, preventing AI hallucinations."
            )
        ]
    },
    {
        "name": "MEMBER 5: MUHAMMAD ABDULLAH (Roll No: BSDSF23A032)",
        "role": "Lead Web Portal UI, DuckDB Fleet Analytics & Regional Market Pricing Specialist",
        "stat": "30 Tickets | 124 Story Points | Sprints 1 to 4 Done, Sprints 5 & 6 To Do",
        "simple_summary": "I am the frontend designer, price calculator, and fleet analytics specialist. I built the modern React 18 Web Portal with dark mode, interactive diagnostic terminals, and live telemetry tickers. I also built the Pakistani Fair-Price Market Estimator that calculates real parts and labor costs in Pakistani Rupees (PKR) across Lahore, Karachi, and Islamabad, and integrated the DuckDB in-memory engine to run complex analytical queries over 500,000 vehicle records in less than 80 milliseconds.",
        "what_built_detail": [
            "Modern React 18 Engineering Web Portal: Built with Tailwind CSS, featuring an interactive diagnostic console, 4-stage architecture explainer, and quick scenario cards.",
            "Pakistani Fair-Price Market Estimator: Verified parts and labor database in PKR covering genuine OEM, quality aftermarket, and Kabli parts across Pakistani cities.",
            "DuckDB In-Memory OLAP Query Engine: Vectorized columnar query engine executing analytical aggregations across 500,000 rows in < 80ms (15x faster than SQLite).",
            "Regional Climate Wear Multipliers: Degradation formulas factoring in extreme Pakistani summer heat (45°C+ in Lahore/Multan) and dusty roads to forecast accurate part lifespans."
        ],
        "scenarios": [
            (
                "Tough Question 1: 'Why does your portal show car repair prices in PKR? Where did you get this data, and how do you prevent fake estimates?'",
                "Sir, most foreign automotive apps show USD prices that are completely meaningless in Pakistan. We conducted field research across major Pakistani auto spare parts markets (Bilal Gunj in Lahore, Shershah in Karachi, and Rawalpindi). We indexed verified price ranges for Genuine OEM, Brand-New Aftermarket (e.g. Denso/NGK), and Grade-A Kabli replacement parts alongside standard workshop labor hours in PKR. Our model provides low, median, and high estimates so customers know the realistic market price before walking into a workshop."
            ),
            (
                "Tough Question 2: 'Why did you use DuckDB instead of standard SQLite or MySQL for your analytics?'",
                "Sir, traditional relational databases like SQLite and MySQL are row-oriented. When running fleet analytics (for example: calculating average coolant temperature across 500,000 vehicle trips grouped by car model), a row-oriented database reads the entire row from disk, causing massive latency. DuckDB is a modern columnar analytical engine. It reads only the target columns in compressed Snappy Parquet format using SIMD vectorized execution, achieving over a 15x speedup and executing complex fleet queries in under 80 milliseconds!"
            ),
            (
                "Tough Question 3: 'How does Pakistani weather affect your maintenance prediction?'",
                "Sir, international manufacturer service handbooks assume European or Japanese climates (20°C ambient temperature). In Pakistan, summer temperatures exceed 45°C in Lahore and Multan, and urban traffic involves severe stop-and-go driving with airborne dust. I formulated Pakistani Climate Risk Multipliers (AUT-118) that apply a 1.25x degradation acceleration factor to radiator coolant, air filters, and transmission oils, warning Pakistani owners to service components 25% earlier to avoid engine seizure."
            )
        ]
    }
]
