# multi-source knowledge base

- `author`: novel
- `teacher`: 
    - resources for teacher experts in the T-Group.
    - `books`: novel
    - `record`: class recordings
    - `theory`: books of educational theories
- `psycho`:
    - resources for educational psychologists in the P-Group.
    - `text`: books of educational psychology theories


## vector database by Chromadb

**The vector databases are huge, so we don't upload them to the repository. You can use `get_vec_db` function to create them.**

- `novel_db`: vector base of the novel *Robinson Crusoe* for teacher experts.

- `psy_theory_db`: vector base of educational psychology theories for educational psychologists.

- `edu_theory_db`: vector base of educational theories for teacher experts.

- `record_db`: vector base of class recordings for teacher experts.