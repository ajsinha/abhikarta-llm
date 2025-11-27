/**
 * Custom Table Pagination Helper
 *
 * Copyright © 2025-2030, All Rights Reserved
 * Ashutosh Sinha | Email: ajsinha@gmail.com
 */

class TablePagination {
    constructor(tableId, options = {}) {
        this.table = document.getElementById(tableId);
        if (!this.table) {
            console.error(`Table with id "${tableId}" not found`);
            return;
        }

        this.tbody = this.table.querySelector('tbody');
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));
        this.currentPage = 1;
        this.rowsPerPage = options.defaultRowsPerPage || 10;
        this.tableId = tableId;

        this.init();
    }

    init() {
        // Create pagination controls
        this.createControls();
        // Initial render
        this.render();
    }

    createControls() {
        // Create top container (before table) for row selector
        const topContainer = document.createElement('div');
        topContainer.id = `${this.tableId}-pagination-top`;
        topContainer.className = 'row mb-3';
        topContainer.innerHTML = `
            <div class="col-md-12">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                        <label class="me-2 mb-0">Show</label>
                        <select class="form-select form-select-sm" style="width: auto;" id="${this.tableId}-rows-select">
                            <option value="5">5</option>
                            <option value="10" ${this.rowsPerPage === 10 ? 'selected' : ''}>10</option>
                            <option value="25">25</option>
                            <option value="50">50</option>
                            <option value="all">ALL</option>
                        </select>
                        <label class="ms-2 mb-0">entries</label>
                    </div>
                    <div>
                        <span class="text-muted" id="${this.tableId}-info"></span>
                    </div>
                </div>
            </div>
        `;

        // Create bottom container (after table) for pagination links
        const bottomContainer = document.createElement('div');
        bottomContainer.id = `${this.tableId}-pagination-bottom`;
        bottomContainer.className = 'row mt-3';
        bottomContainer.innerHTML = `
            <div class="col-md-12">
                <nav aria-label="Table pagination">
                    <ul class="pagination pagination-sm justify-content-end mb-0" id="${this.tableId}-pagination">
                    </ul>
                </nav>
            </div>
        `;

        // Insert top container before table
        this.table.parentElement.insertBefore(topContainer, this.table);

        // Insert bottom container after table
        this.table.parentElement.appendChild(bottomContainer);

        // Add event listener for rows per page
        document.getElementById(`${this.tableId}-rows-select`).addEventListener('change', (e) => {
            const value = e.target.value;
            this.rowsPerPage = value === 'all' ? this.rows.length : parseInt(value);
            this.currentPage = 1;
            this.render();
        });
    }

    render() {
        const totalRows = this.rows.length;
        const totalPages = Math.ceil(totalRows / this.rowsPerPage);

        // Hide all rows first
        this.rows.forEach(row => row.style.display = 'none');

        // Calculate start and end indices
        const start = (this.currentPage - 1) * this.rowsPerPage;
        const end = Math.min(start + this.rowsPerPage, totalRows);

        // Show current page rows
        for (let i = start; i < end; i++) {
            this.rows[i].style.display = '';
        }

        // Update info text
        const infoText = totalRows === 0
            ? 'No entries found'
            : `Showing ${start + 1} to ${end} of ${totalRows} entries`;
        document.getElementById(`${this.tableId}-info`).textContent = infoText;

        // Render pagination links
        this.renderPagination(totalPages);
    }

    renderPagination(totalPages) {
        const paginationContainer = document.getElementById(`${this.tableId}-pagination`);
        paginationContainer.innerHTML = '';

        if (totalPages <= 1) {
            return; // No pagination needed
        }

        // Previous button
        const prevLi = this.createPageItem('Previous', this.currentPage - 1, this.currentPage === 1);
        paginationContainer.appendChild(prevLi);

        // Page numbers
        const pages = this.getPageNumbers(totalPages);
        pages.forEach(page => {
            if (page === '...') {
                const li = document.createElement('li');
                li.className = 'page-item disabled';
                li.innerHTML = '<span class="page-link">...</span>';
                paginationContainer.appendChild(li);
            } else {
                const li = this.createPageItem(page, page, false, page === this.currentPage);
                paginationContainer.appendChild(li);
            }
        });

        // Next button
        const nextLi = this.createPageItem('Next', this.currentPage + 1, this.currentPage === totalPages);
        paginationContainer.appendChild(nextLi);
    }

    createPageItem(text, page, disabled, active = false) {
        const li = document.createElement('li');
        li.className = `page-item ${disabled ? 'disabled' : ''} ${active ? 'active' : ''}`;

        const link = document.createElement('a');
        link.className = 'page-link';
        link.href = '#';
        link.textContent = text;

        if (!disabled) {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.currentPage = page;
                this.render();
            });
        }

        li.appendChild(link);
        return li;
    }

    getPageNumbers(totalPages) {
        const pages = [];
        const maxVisible = 5;

        if (totalPages <= maxVisible) {
            // Show all pages
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            // Show with ellipsis
            if (this.currentPage <= 3) {
                // Near start
                for (let i = 1; i <= 4; i++) {
                    pages.push(i);
                }
                pages.push('...');
                pages.push(totalPages);
            } else if (this.currentPage >= totalPages - 2) {
                // Near end
                pages.push(1);
                pages.push('...');
                for (let i = totalPages - 3; i <= totalPages; i++) {
                    pages.push(i);
                }
            } else {
                // In middle
                pages.push(1);
                pages.push('...');
                for (let i = this.currentPage - 1; i <= this.currentPage + 1; i++) {
                    pages.push(i);
                }
                pages.push('...');
                pages.push(totalPages);
            }
        }

        return pages;
    }

    // Public method to refresh pagination (e.g., after filtering)
    refresh() {
        this.rows = Array.from(this.tbody.querySelectorAll('tr'));
        this.currentPage = 1;
        this.render();
    }
}

// Auto-initialize tables with data-pagination attribute
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('table[data-pagination="true"]').forEach(table => {
        const defaultRows = table.getAttribute('data-default-rows') || 10;
        new TablePagination(table.id, { defaultRowsPerPage: parseInt(defaultRows) });
    });
});