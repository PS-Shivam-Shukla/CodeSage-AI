"""
Configuration for document chunking.

Keeping configuration separate from implementation makes it
easy to experiment with different chunking strategies without
changing the splitter logic.

Optimized for better semantic focus and retrieval performance.
"""

# Maximum characters allowed in a chunk
# Reduced from 1000 to 600 for better semantic focus and retrieval precision
# Smaller chunks = more focused semantic meaning = better vector matching
DEFAULT_CHUNK_SIZE = 600

# Number of overlapping characters
# Increased from 200 to 150 to maintain context between chunks
# 25% overlap provides good continuity without excessive duplication
DEFAULT_CHUNK_OVERLAP = 150

# Ordered from highest priority to lowest priority.
# The RecursiveCharacterTextSplitter will try these one by one.
# Optimized separators for Python codebases with better granularity
DEFAULT_SEPARATORS = [
    # Python class definitions (highest priority - major semantic boundaries)
    "\nclass ",
    "\n@dataclass",
    "\n@abstractmethod",
    
    # Python function definitions
    "\ndef ",
    "\nasync def ",
    "\n    def ",  # Indented methods
    
    # Python decorators and special constructs
    "\n@staticmethod",
    "\n@classmethod",
    "\n@property",
    
    # Other language constructs
    "\npublic ",
    "\nprivate ",
    "\nprotected ",
    "\nfunction ",
    "\ninterface ",
    "\nenum ",
    
    # Documentation and comments (secondary boundaries)
    "\n\"\"\"\n",  # Docstring ends
    "\n# ===",     # Section markers
    "\n# ---",     # Subsection markers
    
    # Paragraph and sentence boundaries
    "\n\n",        # Double newline (paragraph break)
    "\n",          # Single newline
    ". ",          # Sentence boundary
    " ",           # Word boundary
    "",            # Character boundary (fallback)
]