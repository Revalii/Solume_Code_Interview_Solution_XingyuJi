/*
App.jsx

Main React component for the healthcare facility mortality dashboard.

Responsibilities:
- Manage global state (filters, summary, table, analysis)
- Handle API calls to backend endpoints
- Control page navigation (Summary / Analysis)
- Pass data to UI components

Author: Xingyu Ji
 */

import {useEffect, useState} from "react";

const API_BASE = "http://127.0.0.1:8000";

const YEARS = ["", "2021", "2022", "2023", "2024"];
const MONTHS = [
    {value: "", label: "All"},
    {value: "1", label: "Jan"},
    {value: "2", label: "Feb"},
    {value: "3", label: "Mar"},
    {value: "4", label: "Apr"},
    {value: "5", label: "May"},
    {value: "6", label: "Jun"},
    {value: "7", label: "Jul"},
    {value: "8", label: "Aug"},
    {value: "9", label: "Sep"},
    {value: "10", label: "Oct"},
    {value: "11", label: "Nov"},
    {value: "12", label: "Dec"},
];

const STATES = [
    "",
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD",
    "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH",
    "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY",
];

const EMPTY_FILTERS = {
    year: "",
    month: "",
    state: "",
    zip_code: "",
    facility_name: "",
};

const TABLE_COLUMNS = [
    {key: "ccn", label: "CCN", sortable: true},
    {key: "facility_name", label: "Facility Name", sortable: true},
    {key: "city", label: "City", sortable: true},
    {key: "state", label: "State", sortable: true},
    {key: "zip_code", label: "ZIP", sortable: true},
    {key: "mortality_rate", label: "Mortality Rate", sortable: true},
    {key: "patient_count", label: "Patient Count", sortable: true},
    {key: "mortality_category", label: "Category", sortable: false},
];

// Convert value to number safely
function toFiniteNumber(value) {
    const num = Number(value);
    return Number.isFinite(num) ? num : null;
}

// Format metric for display (2 decimal places or N/A)
function formatMetric(value) {
    const num = toFiniteNumber(value);
    return num === null ? "N/A" : num.toFixed(2);
}

// Generate unique key for table/list rendering
function makeDisplayRowKey(row, index) {
    return `${row.ccn || "ccn"}-${row.smr_date || "date"}-${row.facility_name || "facility"}-${index}`;
}

// Build API URL with filters
function buildUrl(path, filters, extraParams = {}) {
    const params = new URLSearchParams();

    Object.entries(extraParams).forEach(([key, value]) => {
        if (value !== "" && value !== null && value !== undefined) {
            params.append(key, String(value));
        }
    });

    if (filters.year) params.append("year", filters.year);
    if (filters.month) params.append("month", filters.month);
    if (filters.state) params.append("state", filters.state);
    if (filters.zip_code.trim()) params.append("zip_code", filters.zip_code.trim());
    if (filters.facility_name.trim()) params.append("facility_name", filters.facility_name.trim());

    return `${API_BASE}${path}?${params.toString()}`;
}

// Generic fetch wrapper with error handling
async function fetchJson(url, fallbackMessage) {
    const response = await fetch(url);

    if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || fallbackMessage);
    }

    return response.json();
}

function NavBar({activePage, setActivePage}) {
    return (
        <div style={styles.navBar}>
            <button
                style={{
                    ...styles.navButton,
                    ...(activePage === "summary" ? styles.navButtonActive : {}),
                }}
                onClick={() => setActivePage("summary")}
            >
                Summary Page
            </button>

            <button
                style={{
                    ...styles.navButton,
                    ...(activePage === "analysis" ? styles.navButtonActive : {}),
                }}
                onClick={() => setActivePage("analysis")}
            >
                Analysis Page
            </button>
        </div>
    );
}

function FilterPanel({filters, setFilters, onApply, onReset}) {
    function handleChange(event) {
        const {name, value} = event.target;

        setFilters((prev) => {
            const next = {...prev, [name]: value};
            if (name === "year" && value === "") {
                next.month = "";
            }
            return next;
        });
    }

    return (
        <section style={styles.section}>
            <h2 style={styles.sectionTitle}>Filters</h2>

            <div style={styles.filterGrid}>
                <div style={styles.field}>
                    <label style={styles.label}>Year</label>
                    <select name="year" value={filters.year} onChange={handleChange} style={styles.input}>
                        <option value="">All</option>
                        {YEARS.filter(Boolean).map((year) => (
                            <option key={year} value={year}>
                                {year}
                            </option>
                        ))}
                    </select>
                </div>

                <div style={styles.field}>
                    <label style={styles.label}>Month</label>
                    <select
                        name="month"
                        value={filters.month}
                        onChange={handleChange}
                        style={styles.input}
                        disabled={!filters.year}
                    >
                        {MONTHS.map((month) => (
                            <option key={month.value || "all"} value={month.value}>
                                {month.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div style={styles.field}>
                    <label style={styles.label}>State</label>
                    <select name="state" value={filters.state} onChange={handleChange} style={styles.input}>
                        <option value="">All</option>
                        {STATES.filter(Boolean).map((state) => (
                            <option key={state} value={state}>
                                {state}
                            </option>
                        ))}
                    </select>
                </div>

                <div style={styles.field}>
                    <label style={styles.label}>ZIP Code</label>
                    <input
                        name="zip_code"
                        type="text"
                        value={filters.zip_code}
                        onChange={handleChange}
                        placeholder="e.g. 35233"
                        style={styles.input}
                    />
                </div>

                <div style={{...styles.field, gridColumn: "span 2"}}>
                    <label style={styles.label}>Facility Name</label>
                    <input
                        name="facility_name"
                        type="text"
                        value={filters.facility_name}
                        onChange={handleChange}
                        placeholder="Search facility name"
                        style={styles.input}
                    />
                </div>
            </div>

            <div style={styles.buttonRow}>
                <button onClick={onApply} style={styles.primaryButton}>
                    Apply Filters
                </button>
                <button onClick={onReset} style={styles.secondaryButton}>
                    Reset
                </button>
            </div>
        </section>
    );
}

function StatCard({label, value}) {
    return (
        <div style={styles.statCard}>
            <div style={styles.statLabel}>{label}</div>
            <div style={styles.statValue}>{value}</div>
        </div>
    );
}

function FacilityList({title, items}) {
    return (
        <div style={styles.listCard}>
            <h3 style={styles.sectionSubTitle}>{title}</h3>

            {items.length === 0 ? (
                <p style={styles.emptyText}>No data available.</p>
            ) : (
                <ol style={styles.list}>
                    {items.map((item, index) => (
                        <li key={makeDisplayRowKey(item, index)} style={styles.listItem}>
                            <span>{item.facility_name}</span>
                            <span style={styles.rateText}>{formatMetric(item.mortality_rate)}</span>
                        </li>
                    ))}
                </ol>
            )}
        </div>
    );
}

function SortableTh({column, activeSort, sortOrder, onSort}) {
    const isActive = activeSort === column.key;
    const arrow = !isActive ? "↕" : sortOrder === "asc" ? "↑" : "↓";

    return (
        <th style={styles.th}>
            <button
                type="button"
                onClick={() => onSort(column.key)}
                style={{
                    ...styles.sortButton,
                    ...(isActive ? styles.sortButtonActive : {}),
                }}
            >
                <span>{column.label}</span>
                <span style={styles.sortArrow}>{arrow}</span>
            </button>
        </th>
    );
}

function SummaryPage({
                         summary,
                         loading,
                         error,
                         warning,
                         progress,
                         tableData,
                         tableLoading,
                         tableError,
                         onTablePageChange,
                         onTableSort,
                     }) {
    return (
        <>
            <h1 style={styles.pageTitle}>Summary</h1>

            <section style={styles.section}>
                <h2 style={styles.sectionTitle}>Display</h2>

                {loading && (
                    <p style={styles.loadingText}>
                        Loading data... page {progress.page}, {progress.loaded} rows loaded
                        {progress.expectedTotal ? ` / ${progress.expectedTotal}` : ""}
                    </p>
                )}

                {error && <p style={styles.errorText}>Error: {error}</p>}
                {warning && !error && <p style={styles.warningText}>Warning: {warning}</p>}

                {!loading && !error && (
                    <>
                        <div style={styles.statsGrid}>
                            <StatCard label="Total Facilities" value={summary.total}/>
                            <StatCard label="Average Mortality Rate" value={formatMetric(summary.avgMortality)}/>
                            <StatCard label="Max Mortality Rate" value={formatMetric(summary.maxMortality)}/>
                            <StatCard label="Min Mortality Rate" value={formatMetric(summary.minMortality)}/>
                        </div>

                        <div style={styles.listGrid}>
                            <FacilityList title="Top 10 Highest Mortality Facilities" items={summary.top10Highest}/>
                            <FacilityList title="Top 10 Lowest Mortality Facilities" items={summary.top10Lowest}/>
                        </div>

                        <div style={styles.tableWrapper}>
                            <div style={styles.tableHeaderRow}>
                                <div/>
                                <h3 style={styles.tableTitle}>Full Data Table</h3>
                                <span style={styles.tableMetaText}>
        Page {tableData.page} of {tableData.totalPages} · {tableData.total} records
    </span>
                            </div>

                            <div style={styles.tableBox}>
                                <div style={styles.responsiveTable}>
                                    <table style={styles.table}>
                                        <thead>
                                        <tr>
                                            {TABLE_COLUMNS.map((column) =>
                                                column.sortable ? (
                                                    <SortableTh
                                                        key={column.key}
                                                        column={column}
                                                        activeSort={tableData.sortBy}
                                                        sortOrder={tableData.sortOrder}
                                                        onSort={onTableSort}
                                                    />
                                                ) : (
                                                    <th key={column.key} style={styles.th}>
                                                        {column.label}
                                                    </th>
                                                )
                                            )}
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {tableLoading ? (
                                            <tr>
                                                <td style={styles.emptyTableCell} colSpan={TABLE_COLUMNS.length}>
                                                    Loading table data...
                                                </td>
                                            </tr>
                                        ) : tableError ? (
                                            <tr>
                                                <td style={styles.emptyTableCell} colSpan={TABLE_COLUMNS.length}>
                                                    Error: {tableError}
                                                </td>
                                            </tr>
                                        ) : tableData.rows.length === 0 ? (
                                            <tr>
                                                <td style={styles.emptyTableCell} colSpan={TABLE_COLUMNS.length}>
                                                    No table data found for the current filters.
                                                </td>
                                            </tr>
                                        ) : (
                                            tableData.rows.map((row, index) => (
                                                <tr key={makeDisplayRowKey(row, `${tableData.page}-${index}`)}>
                                                    <td style={styles.td}>{row.ccn || "N/A"}</td>
                                                    <td style={styles.td}>{row.facility_name || "N/A"}</td>
                                                    <td style={styles.td}>{row.city || "N/A"}</td>
                                                    <td style={styles.td}>{row.state || "N/A"}</td>
                                                    <td style={styles.td}>{row.zip_code || "N/A"}</td>
                                                    <td style={styles.td}>{formatMetric(row.mortality_rate)}</td>
                                                    <td style={styles.td}>{toFiniteNumber(row.patient_count) ?? "N/A"}</td>
                                                    <td style={styles.td}>{row.mortality_category || "N/A"}</td>
                                                </tr>
                                            ))
                                        )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <div style={styles.paginationRow}>
                                <button
                                    style={{
                                        ...styles.secondaryButton,
                                        ...(tableData.page <= 1 ? styles.buttonDisabled : {}),
                                    }}
                                    onClick={() => onTablePageChange(tableData.page - 1)}
                                    disabled={tableData.page <= 1 || tableLoading}
                                >
                                    Previous
                                </button>

                                <span style={styles.pageText}>
                  Page {tableData.page} of {tableData.totalPages}
                </span>

                                <button
                                    style={{
                                        ...styles.secondaryButton,
                                        ...(tableData.page >= tableData.totalPages ? styles.buttonDisabled : {}),
                                    }}
                                    onClick={() => onTablePageChange(tableData.page + 1)}
                                    disabled={tableData.page >= tableData.totalPages || tableLoading}
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </section>
        </>
    );
}

function SimpleBarChart({title, items, labelKey, valueKey, valueFormatter}) {
    const maxValue = Math.max(...items.map((item) => Number(item[valueKey] || 0)), 0);

    return (
        <div style={styles.chartCard}>
            <h3 style={styles.sectionSubTitle}>{title}</h3>

            {items.length === 0 ? (
                <p style={styles.emptyText}>No data available.</p>
            ) : (
                <div style={styles.barChartList}>
                    {items.map((item, index) => {
                        const value = Number(item[valueKey] || 0);
                        const width = maxValue === 0 ? 0 : (value / maxValue) * 100;

                        return (
                            <div key={`${item[labelKey]}-${index}`} style={styles.barRow}>
                                <div style={styles.barLabel}>{item[labelKey]}</div>
                                <div style={styles.barTrack}>
                                    <div style={{...styles.barFill, width: `${width}%`}}/>
                                </div>
                                <div style={styles.barValue}>{valueFormatter ? valueFormatter(value) : value}</div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

function AnalysisPage({analysisData, summaryData, loading, error, warning}) {
    const stateRows = analysisData.byState.slice(0, 10);
    const zipRows = analysisData.byZip.slice(0, 10);
    const distributionRows = analysisData.distribution;
    const rankingRows = summaryData.top10Highest;

    return (
        <>
            <h1 style={styles.pageTitle}>Analysis</h1>

            <section style={styles.section}>
                <h2 style={styles.sectionTitle}>Analysis</h2>

                {loading && <p style={styles.loadingText}>Loading analysis data...</p>}
                {error && <p style={styles.errorText}>Error: {error}</p>}
                {warning && !error && <p style={styles.warningText}>Warning: {warning}</p>}

                {!loading && !error && (
                    <div style={styles.analysisGrid}>
                        <SimpleBarChart
                            title="Mortality Comparison by State"
                            items={stateRows}
                            labelKey="state"
                            valueKey="avgMortality"
                            valueFormatter={(value) => (Number.isNaN(value) ? "N/A" : value.toFixed(2))}
                        />

                        <SimpleBarChart
                            title="Mortality Comparison by ZIP Code"
                            items={zipRows}
                            labelKey="zip_code"
                            valueKey="avgMortality"
                            valueFormatter={(value) => (Number.isNaN(value) ? "N/A" : value.toFixed(2))}
                        />

                        <SimpleBarChart
                            title="Distribution"
                            items={distributionRows}
                            labelKey="range"
                            valueKey="count"
                        />

                        <div style={styles.chartCard}>
                            <h3 style={styles.sectionSubTitle}>Facility Ranking Table</h3>
                            <div style={styles.tableBox}>
                                <div style={styles.responsiveTable}>
                                    <table style={styles.table}>
                                        <thead>
                                        <tr>
                                            <th style={styles.th}>Rank</th>
                                            <th style={styles.th}>Facility Name</th>
                                            <th style={styles.th}>State</th>
                                            <th style={styles.th}>ZIP</th>
                                            <th style={styles.th}>Mortality Rate</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {rankingRows.length === 0 ? (
                                            <tr>
                                                <td style={styles.emptyTableCell} colSpan={5}>
                                                    No ranking data available.
                                                </td>
                                            </tr>
                                        ) : (
                                            rankingRows.map((item, index) => (
                                                <tr key={makeDisplayRowKey(item, index)}>
                                                    <td style={styles.td}>{index + 1}</td>
                                                    <td style={styles.td}>{item.facility_name || "N/A"}</td>
                                                    <td style={styles.td}>{item.state || "N/A"}</td>
                                                    <td style={styles.td}>{item.zip_code || "N/A"}</td>
                                                    <td style={styles.td}>{formatMetric(item.mortality_rate)}</td>
                                                </tr>
                                            ))
                                        )}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </section>
        </>
    );
}

export default function App() {
    const [activePage, setActivePage] = useState("summary");
    const [filters, setFilters] = useState(EMPTY_FILTERS);

    // summary
    const [summaryData, setSummaryData] = useState({
        total: 0,
        avgMortality: null,
        minMortality: null,
        maxMortality: null,
        top10Highest: [],
        top10Lowest: [],
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [warning, setWarning] = useState("");
    const [progress] = useState({page: 1, loaded: 0, expectedTotal: null});

    // table
    const [tableData, setTableData] = useState({
        rows: [],
        total: 0,
        page: 1,
        pageSize: 10,
        totalPages: 1,
        sortBy: "mortality_rate",
        sortOrder: "desc",
    });
    const [tableLoading, setTableLoading] = useState(false);
    const [tableError, setTableError] = useState("");

    // analysis
    const [analysisData, setAnalysisData] = useState({
        byState: [],
        byZip: [],
        distribution: [],
    });
    const [analysisLoading, setAnalysisLoading] = useState(false);
    const [analysisError, setAnalysisError] = useState("");

    useEffect(() => {
        handleApply();
    }, []);

    // Fetch summary data
    async function fetchSummary(currentFilters) {
        const data = await fetchJson(
            buildUrl("/summary", currentFilters),
            "Failed to fetch summary data"
        );

        setSummaryData({
            total: data.total ?? 0,
            avgMortality: data.avgMortality ?? null,
            minMortality: data.minMortality ?? null,
            maxMortality: data.maxMortality ?? null,
            top10Highest: data.top10Highest ?? [],
            top10Lowest: data.top10Lowest ?? [],
        });
    }

    // Fetch table data
    async function fetchTable(
        currentFilters,
        page = 1,
        sortBy = tableData.sortBy,
        sortOrder = tableData.sortOrder
    ) {
        setTableLoading(true);
        setTableError("");

        try {
            const data = await fetchJson(
                buildUrl("/table", currentFilters, {
                    page,
                    pageSize: 10,
                    sortBy,
                    sortOrder,
                }),
                "Failed to fetch table data"
            );

            const nextRows = data.data ?? [];
            const nextTotal = data.total ?? 0;
            const nextPage = data.page ?? page;
            const nextPageSize = data.pageSize ?? 10;
            const nextTotalPages = Math.max(1, Math.ceil(nextTotal / nextPageSize));

            setTableData({
                rows: nextRows,
                total: nextTotal,
                page: nextPage,
                pageSize: nextPageSize,
                totalPages: nextTotalPages,
                sortBy,
                sortOrder,
            });
        } catch (err) {
            setTableError(err.message || "Failed to fetch table data");
        } finally {
            setTableLoading(false);
        }
    }

    // Fetch analysis data
    async function fetchAnalysis(currentFilters) {
        setAnalysisLoading(true);
        setAnalysisError("");

        try {
            const data = await fetchJson(
                buildUrl("/analysis", currentFilters),
                "Failed to fetch analysis data"
            );

            setAnalysisData({
                byState: data.byState ?? [],
                byZip: data.byZip ?? [],
                distribution: data.distribution ?? [],
            });
        } catch (err) {
            setAnalysisError(err.message || "Failed to fetch analysis data");
        } finally {
            setAnalysisLoading(false);
        }
    }

    // Apply filters → fetch all data
    async function handleApply() {
        setLoading(true);
        setError("");
        setWarning("");
        setTableError("");
        setAnalysisError("");

        try {
            await fetchSummary(filters);
            await fetchTable(filters, 1, "mortality_rate", "desc");
            await fetchAnalysis(filters);
        } catch (err) {
            setError(err.message || "Failed to fetch data");
        } finally {
            setLoading(false);
        }
    }

    async function handleTablePageChange(nextPage) {
        await fetchTable(filters, nextPage, tableData.sortBy, tableData.sortOrder);
    }

    async function handleTableSort(columnKey) {
        const nextOrder =
            tableData.sortBy === columnKey
                ? tableData.sortOrder === "asc"
                    ? "desc"
                    : "asc"
                : "asc";

        await fetchTable(filters, 1, columnKey, nextOrder);
    }

    function handleReset() {
        setFilters(EMPTY_FILTERS);

        setSummaryData({
            total: 0,
            avgMortality: null,
            minMortality: null,
            maxMortality: null,
            top10Highest: [],
            top10Lowest: [],
        });

        setTableData({
            rows: [],
            total: 0,
            page: 1,
            pageSize: 10,
            totalPages: 1,
            sortBy: "mortality_rate",
            sortOrder: "desc",
        });

        setAnalysisData({
            byState: [],
            byZip: [],
            distribution: [],
        });

        setError("");
        setWarning("");
        setTableError("");
        setAnalysisError("");
    }

    return (
        <div style={styles.page}>
            <div style={styles.container}>
                <NavBar activePage={activePage} setActivePage={setActivePage}/>

                <FilterPanel
                    filters={filters}
                    setFilters={setFilters}
                    onApply={handleApply}
                    onReset={handleReset}
                />

                {activePage === "summary" && (
                    <SummaryPage
                        summary={summaryData}
                        loading={loading}
                        error={error}
                        warning={warning}
                        progress={progress}
                        tableData={tableData}
                        tableLoading={tableLoading}
                        tableError={tableError}
                        onTablePageChange={handleTablePageChange}
                        onTableSort={handleTableSort}
                    />
                )}

                {activePage === "analysis" && (
                    <AnalysisPage
                        analysisData={analysisData}
                        summaryData={summaryData}
                        loading={analysisLoading}
                        error={analysisError}
                        warning={warning}
                    />
                )}
            </div>
        </div>
    );
}

const styles = {
    page: {
        minHeight: "100vh",
        backgroundColor: "#f5f7fb",
        padding: "32px 20px",
        fontFamily: "Arial, sans-serif",
        color: "#1f2937",
    },
    container: {
        maxWidth: "1200px",
        margin: "0 auto",
    },
    navBar: {
        display: "flex",
        gap: "12px",
        marginBottom: "24px",
        backgroundColor: "#ffffff",
        padding: "14px",
        borderRadius: 0,
        boxShadow: "0 6px 18px rgba(0, 0, 0, 0.08)",
    },
    navButton: {
        border: "none",
        backgroundColor: "#e5e7eb",
        color: "#111827",
        padding: "12px 18px",
        borderRadius: 0,
        cursor: "pointer",
        fontWeight: 700,
        fontSize: "15px",
    },
    navButtonActive: {
        backgroundColor: "#0f4c6e",
        color: "#ffffff",
    },
    pageTitle: {
        fontSize: "40px",
        marginBottom: "28px",
        color: "#0f4c6e",
        fontWeight: 700,
    },
    section: {
        backgroundColor: "#ffffff",
        borderRadius: 0,
        padding: "24px",
        marginBottom: "24px",
        boxShadow: "0 6px 18px rgba(0, 0, 0, 0.08)",
    },
    sectionTitle: {
        fontSize: "24px",
        marginBottom: "20px",
        color: "#0f4c6e",
        fontStyle: "italic",
    },
    sectionSubTitle: {
        marginTop: 0,
        marginBottom: "14px",
        color: "#0f4c6e",
    },
    filterGrid: {
        display: "grid",
        gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
        gap: "16px",
    },
    field: {
        display: "flex",
        flexDirection: "column",
        gap: "8px",
    },
    label: {
        fontWeight: 600,
    },
    input: {
        padding: "12px 14px",
        borderRadius: 0,
        border: "1px solid #cbd5e1",
        fontSize: "15px",
        outline: "none",
    },
    buttonRow: {
        display: "flex",
        gap: "12px",
        marginTop: "20px",
    },
    primaryButton: {
        backgroundColor: "#0f4c6e",
        color: "#ffffff",
        border: "none",
        padding: "12px 18px",
        borderRadius: 0,
        cursor: "pointer",
        fontWeight: 600,
    },
    secondaryButton: {
        backgroundColor: "#e5e7eb",
        color: "#111827",
        border: "none",
        padding: "12px 18px",
        borderRadius: 0,
        cursor: "pointer",
        fontWeight: 600,
    },
    buttonDisabled: {
        opacity: 0.5,
        cursor: "not-allowed",
    },
    loadingText: {
        color: "#0f4c6e",
        fontWeight: 600,
        marginBottom: "16px",
    },
    warningText: {
        color: "#b45309",
        fontWeight: 700,
        marginBottom: "16px",
    },
    errorText: {
        color: "#dc2626",
        fontWeight: 700,
        marginBottom: "16px",
    },
    statsGrid: {
        display: "grid",
        gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
        gap: "16px",
        marginBottom: "24px",
    },
    statCard: {
        backgroundColor: "#eef6fb",
        borderRadius: 0,
        padding: "18px",
        border: "1px solid #d6e7f2",
    },
    statLabel: {
        fontSize: "14px",
        color: "#475569",
        marginBottom: "8px",
    },
    statValue: {
        fontSize: "28px",
        fontWeight: 700,
        color: "#0f4c6e",
    },
    listGrid: {
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "20px",
        marginBottom: "24px",
    },
    listCard: {
        backgroundColor: "#fafafa",
        borderRadius: 0,
        padding: "18px",
        border: "1px solid #e5e7eb",
    },
    list: {
        margin: 0,
        paddingLeft: "18px",
    },
    listItem: {
        marginBottom: "10px",
        display: "flex",
        justifyContent: "space-between",
        gap: "12px",
    },
    rateText: {
        fontWeight: 700,
        color: "#0f4c6e",
        whiteSpace: "nowrap",
    },
    emptyText: {
        color: "#64748b",
    },
    tableWrapper: {
        marginTop: "28px",
        backgroundColor: "#fafafa",
        border: "1px solid #e5e7eb",
        padding: "18px",
        borderRadius: 0,
    },
    tableHeaderRow: {
        display: "grid",
        gridTemplateColumns: "1fr auto 1fr",
        alignItems: "center",
        gap: "16px",
        marginBottom: "14px",
    },
    tableMetaText: {
        color: "#475569",
        fontSize: "14px",
        justifySelf: "end",
    },
    tableBox: {
        border: "1px solid #d1d5db",
        backgroundColor: "#ffffff",
    },
    responsiveTable: {
        width: "100%",
        overflowX: "auto",
    },
    table: {
        width: "100%",
        borderCollapse: "collapse",
        backgroundColor: "#ffffff",
        minWidth: "900px",
    },
    th: {
        padding: "12px",
        borderBottom: "1px solid #d1d5db",
        backgroundColor: "#f8fafc",
        fontSize: "14px",
        verticalAlign: "middle",
        textAlign: "center",
    },
    td: {
        padding: "12px",
        borderBottom: "1px solid #e5e7eb",
        fontSize: "14px",
        verticalAlign: "top",
    },
    emptyTableCell: {
        padding: "24px",
        textAlign: "center",
        color: "#64748b",
        fontSize: "14px",
    },
    sortButton: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        gap: "8px",
        border: "none",
        background: "transparent",
        cursor: "pointer",
        padding: 0,
        fontWeight: 700,
        color: "#1f2937",
        fontSize: "14px",
    },
    sortButtonActive: {
        color: "#0f4c6e",
    },
    sortArrow: {
        fontSize: "16px",
        lineHeight: 1,
    },
    paginationRow: {
        display: "grid",
        gridTemplateColumns: "120px 1fr 120px",
        alignItems: "center",
        marginTop: "16px",
        gap: "16px",
    },
    pageText: {
        fontSize: "14px",
        color: "#475569",
        textAlign: "center",
    },
    analysisGrid: {
        display: "grid",
        gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
        gap: "20px",
    },
    chartCard: {
        backgroundColor: "#fafafa",
        borderRadius: 0,
        padding: "18px",
        border: "1px solid #e5e7eb",
    },
    barChartList: {
        display: "flex",
        flexDirection: "column",
        gap: "12px",
    },
    barRow: {
        display: "grid",
        gridTemplateColumns: "120px 1fr 80px",
        gap: "12px",
        alignItems: "center",
    },
    barLabel: {
        fontSize: "13px",
        color: "#334155",
        wordBreak: "break-word",
    },
    barTrack: {
        height: "14px",
        backgroundColor: "#e5e7eb",
        position: "relative",
        overflow: "hidden",
    },
    barFill: {
        height: "100%",
        backgroundColor: "#0f4c6e",
    },
    barValue: {
        fontSize: "13px",
        fontWeight: 700,
        color: "#0f4c6e",
        textAlign: "right",
    },
    tableTitle: {
        margin: 0,
        color: "#0f4c6e",
        textAlign: "center",
        justifySelf: "center",
    },
};
