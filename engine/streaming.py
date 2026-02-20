"""Streaming support for large datasets."""

from __future__ import annotations

from typing import Iterator, List, Dict, Any

from ..core.models.cell import Cell
from ..core.templates.data import TableData


class StreamingDataIterator:
    """
    Iterator for streaming large datasets.

    Processes data in chunks to avoid loading everything into memory.
    """

    def __init__(
        self,
        data_source: Iterator[Dict[str, Any]],
        chunk_size: int = 1000,
    ) -> None:
        """
        Initialize streaming iterator.

        Args:
            data_source: Iterator yielding row dictionaries
            chunk_size: Number of rows per chunk
        """
        self.data_source = data_source
        self.chunk_size = chunk_size

    def iter_chunks(self) -> Iterator[List[Dict[str, Any]]]:
        """Iterate over data in chunks."""
        chunk = []
        for row in self.data_source:
            chunk.append(row)
            if len(chunk) >= self.chunk_size:
                yield chunk
                chunk = []

        if chunk:
            yield chunk


class StreamingTableData(TableData):
    """
    TableData variant that supports streaming.

    Instead of holding all rows in memory, it can work with iterators.
    """

    def __init__(
        self,
        row_iterator: Iterator[Dict[str, Any]] | None = None,
        chunk_size: int = 1000,
    ) -> None:
        """
        Initialize streaming table data.

        Args:
            row_iterator: Iterator yielding row dictionaries
            chunk_size: Chunk size for streaming
        """
        super().__init__()
        self.row_iterator = row_iterator
        self.chunk_size = chunk_size

    def iter_rows_streaming(self) -> Iterator[Dict[str, Any]]:
        """Iterate over rows in streaming mode."""
        if self.row_iterator:
            return self.row_iterator
        return iter(self.rows)

    def iter_chunks(self) -> Iterator[List[Dict[str, Any]]]:
        """Iterate over data in chunks."""
        if self.row_iterator:
            iterator = StreamingDataIterator(self.row_iterator, self.chunk_size)
            return iterator.iter_chunks()
        else:
            for i in range(0, len(self.rows), self.chunk_size):
                yield self.rows[i:i + self.chunk_size]
