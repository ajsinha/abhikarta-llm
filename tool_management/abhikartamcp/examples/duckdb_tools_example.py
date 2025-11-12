"""
Abhikarta MCP Integration - DuckDB Tools Examples

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates how to use DuckDB tools through the MCP integration.
"""

import asyncio
import logging
from typing import Dict, Any
from tool_management import ToolRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from tool_management.abhikartamcp import (
    AbhikartaMCPToolBuilder,
    MCPRegistryIntegration
)


def extract_data(result):
    """
    Helper function to extract data from ToolResult.
    
    Handles both ToolResult objects (with .data attribute) 
    and dictionary results (with 'data' key).
    """
    if result is None:
        return None
    
    # If it's a ToolResult object with .data attribute
    if hasattr(result, 'data'):
        return result.data
    
    # If it's a dictionary
    if isinstance(result, dict):
        return result.get('data', result)
    
    # Return as-is if neither
    return result





async def example_1_list_duckdb_files():
    """
    Example 1: List Available DuckDB Data Files
    
    This example shows how to discover available CSV, Parquet, and JSON files
    that can be loaded into DuckDB for analysis.
    """
    print("\n" + "="*70)
    print("Example 1: List Available DuckDB Files")
    print("="*70)
    
    # Setup
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="admin123"
    )
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    
    try:
        # Start and sync
        await builder.start()
        integration.sync_tools()
        
        # Get the duckdb_list_files tool
        tool = registry.get("duckdb_list_files:abhikartamcp")
        
        if not tool:
            print("❌ duckdb_list_files tool not found")
            return
        
        print(f"✓ Found tool: {tool.name}")
        print(f"  Description: {tool.description}")
        
        # Example 1a: List all data files
        print("\n--- List All Data Files ---")
        result = await tool.execute_async(
            file_type="all",
            include_metadata=True
        )
        
        if result:
            data = extract_data(result)
            print(f"Data directory: {data.get('data_directory')}")
            print(f"Total files: {data.get('total_files')}")
            
            files = data.get('files', [])
            for file_info in files[:5]:  # Show first 5
                print(f"\n  File: {file_info.get('filename')}")
                print(f"    Type: {file_info.get('file_type')}")
                print(f"    Size: {file_info.get('file_size_human', 'N/A')}")
                print(f"    Modified: {file_info.get('modified_date', 'N/A')}")
        
        # Example 1b: List only CSV files
        print("\n--- List Only CSV Files ---")
        result = await tool.execute_async(
            file_type="csv",
            include_metadata=True
        )
        
        if result:
            data = extract_data(result)
            csv_files = data.get('files', [])
            print(f"Found {len(csv_files)} CSV files")
            for file_info in csv_files[:3]:
                print(f"  - {file_info.get('filename')}")
        
        # Example 1c: List Parquet files
        print("\n--- List Parquet Files ---")
        result = await tool.execute_async(
            file_type="parquet"
        )
        
        if result:
            data = extract_data(result)
            parquet_files = data.get('files', [])
            print(f"Found {len(parquet_files)} Parquet files")
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 1 completed")


async def example_2_describe_table():
    """
    Example 2: Describe Table Schema
    
    Shows how to get detailed schema information about a DuckDB table
    including column types, nullability, and sample data.
    """
    print("\n" + "="*70)
    print("Example 2: Describe Table Schema")
    print("="*70)
    
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="admin123"
    )
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    
    try:
        await builder.start()
        integration.sync_tools()
        
        tool = registry.get("duckdb_describe_table:abhikartamcp")
        
        if not tool:
            print("❌ duckdb_describe_table tool not found")
            return
        
        print(f"✓ Found tool: {tool.name}")
        
        # Example 2a: Basic table description
        print("\n--- Describe 'sales' Table (Basic) ---")
        result = await tool.execute_async(
            table_name="sales"
        )
        
        if result:
            data = extract_data(result)
            print(f"Table: {data.get('table_name')}")
            print(f"Type: {data.get('table_type')}")
            print(f"Row count: {data.get('row_count')}")
            
            print("\nColumns:")
            for col in data.get('columns', [])[:5]:
                print(f"  - {col.get('column_name')}")
                print(f"    Type: {col.get('data_type')}")
                print(f"    Nullable: {col.get('nullable', True)}")
                print(f"    Primary Key: {col.get('is_primary_key', False)}")
        
        # Example 2b: Describe with sample data
        print("\n--- Describe 'customers' Table (With Samples) ---")
        result = await tool.execute_async(
            table_name="customers",
            include_sample_data=True,
            sample_size=10
        )
        
        if result:
            data = extract_data(result)
            print(f"Table: {data.get('table_name')}")
            print(f"Columns: {len(data.get('columns', []))}")
            
            sample_data = data.get('sample_data', [])
            if sample_data:
                print(f"\nSample data ({len(sample_data)} rows):")
                for i, row in enumerate(sample_data[:3], 1):
                    print(f"\n  Row {i}:")
                    for key, value in list(row.items())[:5]:
                        print(f"    {key}: {value}")
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 2 completed")


async def example_3_get_statistics():
    """
    Example 3: Get Column Statistics
    
    Demonstrates how to get comprehensive statistical summaries for
    numeric columns including mean, std dev, percentiles, etc.
    """
    print("\n" + "="*70)
    print("Example 3: Get Column Statistics")
    print("="*70)
    
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="admin123"
    )
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    
    try:
        await builder.start()
        integration.sync_tools()
        
        tool = registry.get("duckdb_get_stats:abhikartamcp")
        
        if not tool:
            print("❌ duckdb_get_stats tool not found")
            return
        
        print(f"✓ Found tool: {tool.name}")
        
        # Example 3a: Stats for all numeric columns
        print("\n--- Statistics for All Numeric Columns ---")
        result = await tool.execute_async(
            table_name="sales",
            include_percentiles=True
        )
        
        if result:
            data = extract_data(result)
            print(f"Table: {data.get('table_name')}")
            print(f"Total rows: {data.get('total_rows')}")
            
            col_stats = data.get('column_statistics', {})
            for col_name, stats in list(col_stats.items())[:3]:
                print(f"\nColumn: {col_name}")
                print(f"  Data type: {stats.get('data_type')}")
                print(f"  Count: {stats.get('count')}")
                print(f"  Null count: {stats.get('null_count', 0)}")
                
                if 'mean' in stats:
                    print(f"  Mean: {stats.get('mean'):.2f}")
                    print(f"  Std Dev: {stats.get('std_dev', 0):.2f}")
                    print(f"  Min: {stats.get('min')}")
                    print(f"  25th %ile: {stats.get('percentile_25', 0):.2f}")
                    print(f"  Median: {stats.get('median', 0):.2f}")
                    print(f"  75th %ile: {stats.get('percentile_75', 0):.2f}")
                    print(f"  Max: {stats.get('max')}")
        
        # Example 3b: Stats for specific columns
        print("\n--- Statistics for Specific Columns ---")
        result = await tool.execute_async(
            table_name="orders",
            columns=["order_amount", "quantity", "discount"],
            include_percentiles=True
        )
        
        if result:
            data = extract_data(result)
            print(f"Analyzing columns: order_amount, quantity, discount")
            
            col_stats = data.get('column_statistics', {})
            for col_name in ["order_amount", "quantity", "discount"]:
                if col_name in col_stats:
                    stats = col_stats[col_name]
                    print(f"\n{col_name}:")
                    print(f"  Range: {stats.get('min')} - {stats.get('max')}")
                    print(f"  Average: {stats.get('mean', 0):.2f}")
        
        # Example 3c: Basic stats without percentiles
        print("\n--- Basic Statistics (No Percentiles) ---")
        result = await tool.execute_async(
            table_name="transactions",
            include_percentiles=False
        )
        
        if result:
            data = extract_data(result)
            print(f"Table: {data.get('table_name')}")
            print("Statistical summary without percentiles computed")
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 3 completed")


async def example_4_aggregate_data():
    """
    Example 4: Aggregate Data with GROUP BY
    
    Shows how to perform aggregation operations like SUM, AVG, COUNT
    with grouping and filtering.
    """
    print("\n" + "="*70)
    print("Example 4: Aggregate Data")
    print("="*70)
    
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="admin123"
    )
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    
    try:
        await builder.start()
        integration.sync_tools()
        
        tool = registry.get("duckdb_aggregate:abhikartamcp")
        
        if not tool:
            print("❌ duckdb_aggregate tool not found")
            return
        
        print(f"✓ Found tool: {tool.name}")
        
        # Example 4a: Simple aggregation with GROUP BY
        print("\n--- Sum Revenue by Region ---")
        result = await tool.execute_async(
            table_name="sales",
            aggregations={
                "revenue": "sum"
            },
            group_by=["region"]
        )
        
        if result:
            data = extract_data(result)
            print(f"Table: {data.get('table_name')}")
            print(f"Grouped by: {data.get('grouped_by')}")
            print(f"Results: {data.get('row_count')} groups")
            
            for row in data.get('results', [])[:5]:
                region = row.get('region')
                sum_revenue = row.get('sum_revenue', 0)
                print(f"  {region}: ${sum_revenue:,.2f}")
        
        # Example 4b: Multiple aggregations with ordering
        print("\n--- Multiple Aggregations with Ordering ---")
        result = await tool.execute_async(
            table_name="orders",
            aggregations={
                "order_amount": "sum",
                "order_id": "count",
                "order_amount": "avg"  # Can have multiple aggs on same column
            },
            group_by=["customer_id"],
            order_by=[
                {"column": "sum_order_amount", "direction": "desc"}
            ],
            limit=10
        )
        
        if result:
            data = extract_data(result)
            print(f"Top 10 customers by total order amount:")
            
            for i, row in enumerate(data.get('results', []), 1):
                customer_id = row.get('customer_id')
                total = row.get('sum_order_amount', 0)
                count = row.get('count_order_id', 0)
                avg = row.get('avg_order_amount', 0)
                print(f"{i}. Customer {customer_id}:")
                print(f"   Total: ${total:,.2f}, Orders: {count}, Avg: ${avg:.2f}")
        
        # Example 4c: Aggregation with HAVING clause
        print("\n--- Aggregate with HAVING Filter ---")
        result = await tool.execute_async(
            table_name="transactions",
            aggregations={
                "amount": "avg",
                "transaction_id": "count"
            },
            group_by=["merchant"],
            having="count_transaction_id > 100",
            limit=20
        )
        
        if result:
            data = extract_data(result)
            print(f"Merchants with > 100 transactions:")
            
            for row in data.get('results', [])[:5]:
                merchant = row.get('merchant')
                avg_amount = row.get('avg_amount', 0)
                count = row.get('count_transaction_id', 0)
                print(f"  {merchant}: {count} txns, avg ${avg_amount:.2f}")
        
        # Example 4d: COUNT DISTINCT
        print("\n--- Count Distinct Values ---")
        result = await tool.execute_async(
            table_name="orders",
            aggregations={
                "customer_id": "count_distinct",
                "order_id": "count"
            },
            group_by=["order_date"]
        )
        
        if result:
            data = extract_data(result)
            print("Unique customers per day:")
            
            for row in data.get('results', [])[:5]:
                date = row.get('order_date')
                unique_customers = row.get('count_distinct_customer_id', 0)
                total_orders = row.get('count_order_id', 0)
                print(f"  {date}: {unique_customers} customers, {total_orders} orders")
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 4 completed")


async def example_5_complete_workflow():
    """
    Example 5: Complete DuckDB Analysis Workflow
    
    Demonstrates a complete workflow: discover files, load data,
    describe schema, get stats, and perform aggregations.
    """
    print("\n" + "="*70)
    print("Example 5: Complete DuckDB Analysis Workflow")
    print("="*70)
    
    builder = AbhikartaMCPToolBuilder()
    builder.configure(
        base_url="http://localhost:3002",
        username="admin",
        password="admin123"
    )
    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, builder)
    
    try:
        await builder.start()
        integration.sync_tools()
        
        # Step 1: Discover available files
        print("\nStep 1: Discover Available Data Files")
        print("-" * 50)
        
        list_tool = registry.get("duckdb_list_files:abhikartamcp")
        if list_tool:
            result = await list_tool.execute_async(file_type="csv")
            if result:
                data = extract_data(result)
                files = data.get('files', [])
                if files:
                    print(f"✓ Found {len(files)} CSV files")
                    target_file = files[0].get('filename')
                    print(f"  Analyzing: {target_file}")
                else:
                    print("❌ No CSV files found")
                    return
        
        # Step 2: Describe table schema
        print("\nStep 2: Describe Table Schema")
        print("-" * 50)
        
        describe_tool = registry.get("duckdb_describe_table:abhikartamcp")
        if describe_tool:
            result = await describe_tool.execute_async(
                table_name="sales",
                include_sample_data=True,
                sample_size=3
            )
            if result:
                data = extract_data(result)
                columns = data.get('columns', [])
                print(f"✓ Table has {len(columns)} columns")
                print(f"  Row count: {data.get('row_count')}")
        
        # Step 3: Get statistical summary
        print("\nStep 3: Get Statistical Summary")
        print("-" * 50)
        
        stats_tool = registry.get("duckdb_get_stats:abhikartamcp")
        if stats_tool:
            result = await stats_tool.execute_async(
                table_name="sales",
                include_percentiles=True
            )
            if result:
                data = extract_data(result)
                col_stats = data.get('column_statistics', {})
                print(f"✓ Statistics computed for {len(col_stats)} columns")
        
        # Step 4: Perform aggregation analysis
        print("\nStep 4: Perform Aggregation Analysis")
        print("-" * 50)
        
        agg_tool = registry.get("duckdb_aggregate:abhikartamcp")
        if agg_tool:
            result = await agg_tool.execute_async(
                table_name="sales",
                aggregations={
                    "revenue": "sum",
                    "quantity": "sum"
                },
                group_by=["product_category"],
                order_by=[
                    {"column": "sum_revenue", "direction": "desc"}
                ],
                limit=5
            )
            if result:
                data = extract_data(result)
                results = data.get('results', [])
                print(f"✓ Top 5 categories by revenue:")
                for i, row in enumerate(results, 1):
                    category = row.get('product_category')
                    revenue = row.get('sum_revenue', 0)
                    quantity = row.get('sum_quantity', 0)
                    print(f"  {i}. {category}: ${revenue:,.2f} ({quantity} units)")
        
        print("\n" + "="*70)
        print("Workflow Summary:")
        print("  1. Discovered data files ✓")
        print("  2. Analyzed table schema ✓")
        print("  3. Computed statistics ✓")
        print("  4. Performed aggregations ✓")
        print("="*70)
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 5 completed")


async def main():
    """Run all DuckDB examples"""
    
    print("="*70)
    print("ABHIKARTA MCP INTEGRATION - DUCKDB TOOLS EXAMPLES")
    print("Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)")
    print("="*70)
    
    try:
        # Run all examples
        await example_1_list_duckdb_files()
        await example_2_describe_table()
        await example_3_get_statistics()
        await example_4_aggregate_data()
        await example_5_complete_workflow()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
