"""
Configuration for document chunking.

Keeping configuration separate from implementation makes it
easy to experiment with different chunking strategies without
changing the splitter logic.
"""

# Maximum characters allowed in a chunk
DEFAULT_CHUNK_SIZE = 1000

# Number of overlapping characters
DEFAULT_CHUNK_OVERLAP = 200

# Ordered from highest priority to lowest priority.
# The RecursiveCharacterTextSplitter will try these one by one.
DEFAULT_SEPARATORS = [
    "\nclass ",
    "\npublic ",
    "\nprivate ",
    "\nprotected ",
    "\ndef ",
    "\nasync def ",
    "\nfunction ",
    "\ninterface ",
    "\nenum ",
    "\n\n",
    "\n",
    " ",
    "",
]