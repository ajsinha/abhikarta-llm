"""
Abhikarta MCP Integration - Yahoo Finance Tools Examples

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)

This example demonstrates how to use Yahoo Finance tools through the MCP integration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from  tool_management.mcp_server_proxy import MCPServerConfig
from tool_management.mcp_server_factory import build_mcp_server_proxy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from tool_management.abhikartamcp import (
    AbhikartaMCPServerProxy,
    MCPRegistryIntegration
)

from tool_management.registry import ToolRegistry

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



async def example_1_search_symbols():
    """
    Example 1: Search for Stock Symbols
    
    Demonstrates how to search for companies and get their ticker symbols.
    """
    print("\n" + "="*70)
    print("Example 1: Search for Stock Symbols")
    print("="*70)

    config = MCPServerConfig()
    config.base_url = "http://localhost:3002"
    config.mcp_endpoint = "/mcp"
    config.login_endpoint = "/api/auth/login"
    config.tool_list_endpoint = "/api/tools/list"
    config.tool_schema_endpoint_template = "/api/tools/{tool_name}/schema"
    config.username = 'admin'
    config.password = 'admin123'
    config.refresh_interval_seconds = 600  # 10 minutes
    config.timeout_seconds = 30.0
    config.tool_name_suffix = ':abhikartamcp'


    mcp_server_proxy = build_mcp_server_proxy('abhikarta', config)

    
    registry = ToolRegistry()
    integration = MCPRegistryIntegration(registry, mcp_server_proxy)

    try:
        await mcp_server_proxy.start()
        integration.sync_tools()
        
        tool = registry.get("yahoo_search_symbols:abhikartamcp")
        
        if not tool:
            print("❌ yahoo_search_symbols tool not found")
            return
        
        print(f"✓ Found tool: {tool.name}")
        print(f"  Description: {tool.description}")
        
        # Example 1a: Search for Apple
        print("\n--- Search for 'Apple' ---")
        result = await tool.execute_async(
            query="Apple",
            limit=5
        )
        
        if result:
            data = extract_data(result)
            if type(data) == str:
                import json
                print(data)
                data = json.loads(data)

            print(f"Query: {data.get('query')}")
            print(f"Results: {data.get('result_count')}")
            
            for i, stock in enumerate(data.get('results', []), 1):
                print(f"\n{i}. {stock.get('name')}")
                print(f"   Symbol: {stock.get('symbol')}")
                print(f"   Exchange: {stock.get('exchange')}")
                print(f"   Type: {stock.get('type')}")
                if stock.get('sector'):
                    print(f"   Sector: {stock.get('sector')}")
        
        # Example 1b: Search for electric vehicle companies
        print("\n--- Search for 'Electric Vehicle' Companies ---")
        result = await tool.execute_async(
            query="electric vehicle",
            limit=10
        )
        
        if result:
            data = extract_data(result)
            print(f"Found {data.get('result_count')} EV-related stocks:")
            
            for stock in data.get('results', [])[:5]:
                symbol = stock.get('symbol')
                name = stock.get('name')
                exchange = stock.get('exchange')
                print(f"  {symbol:6} - {name} ({exchange})")
        
        # Example 1c: Search NASDAQ semiconductor companies
        print("\n--- Search NASDAQ Semiconductor Companies ---")
        result = await tool.execute_async(
            query="semiconductor",
            exchange="NASDAQ",
            limit=15
        )
        
        if result:
            data = extract_data(result)
            print(f"Found {data.get('result_count')} NASDAQ semiconductor stocks:")
            
            for stock in data.get('results', [])[:5]:
                print(f"  {stock.get('symbol'):6} - {stock.get('name')}")
                if stock.get('market_cap'):
                    print(f"         Market Cap: ${stock.get('market_cap'):,.0f}")
        
    finally:
        await mcp_server_proxy.stop()
    
    print("\n✓ Example 1 completed")


async def example_2_get_stock_quotes():
    """
    Example 2: Get Real-Time Stock Quotes
    
    Shows how to retrieve current stock prices and market statistics.
    """
    print("\n" + "="*70)
    print("Example 2: Get Real-Time Stock Quotes")
    print("="*70)
    
    builder = AbhikartaMCPServerProxy()
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
        
        tool = registry.get("yahoo_get_quote:abhikartamcp")
        
        if not tool:
            print("❌ yahoo_get_quote tool not found")
            return
        
        print(f"✓ Found tool: {tool.name}")
        
        # Example 2a: Get Apple stock quote
        print("\n--- Apple Inc. (AAPL) Quote ---")
        result = await tool.execute_async(symbol="AAPL")
        
        if result:
            data = extract_data(result)
            print(f"\n{data.get('name')} ({data.get('symbol')})")
            print(f"{'='*50}")
            
            price = data.get('price', 0)
            change = data.get('change', 0)
            change_pct = data.get('change_percent', 0)
            
            change_symbol = "▲" if change >= 0 else "▼"
            print(f"Price:           ${price:.2f}")
            print(f"Change:          {change_symbol} ${abs(change):.2f} ({change_pct:+.2f}%)")
            print(f"Volume:          {data.get('volume', 0):,}")
            print(f"Market Cap:      ${data.get('market_cap', 0):,.0f}")
            
            print(f"\nDay Range:       ${data.get('day_low', 0):.2f} - ${data.get('day_high', 0):.2f}")
            print(f"52-Week Range:   ${data.get('fifty_two_week_low', 0):.2f} - ${data.get('fifty_two_week_high', 0):.2f}")
            
            if data.get('pe_ratio'):
                print(f"\nP/E Ratio:       {data.get('pe_ratio'):.2f}")
            if data.get('dividend_yield'):
                print(f"Dividend Yield:  {data.get('dividend_yield'):.2f}%")
            
            print(f"\nLast Updated:    {data.get('last_updated')}")
        
        # Example 2b: Get quotes for multiple tech stocks
        print("\n--- Tech Stock Comparison ---")
        
        tech_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
        
        print(f"{'Symbol':<8} {'Price':<12} {'Change':<12} {'Market Cap':<15}")
        print("-" * 55)
        
        for symbol in tech_stocks:
            result = await tool.execute_async(symbol=symbol)
            
            if result:
                data = extract_data(result)
                price = data.get('price', 0)
                change_pct = data.get('change_percent', 0)
                market_cap = data.get('market_cap', 0)
                
                change_str = f"{change_pct:+.2f}%"
                market_cap_str = f"${market_cap/1e9:.1f}B" if market_cap else "N/A"
                
                print(f"{symbol:<8} ${price:<11.2f} {change_str:<12} {market_cap_str:<15}")
            
            # Brief delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        # Example 2c: Get S&P 500 Index
        print("\n--- S&P 500 Index (^GSPC) ---")
        result = await tool.execute_async(symbol="^GSPC")
        
        if result:
            data = extract_data(result)
            price = data.get('price', 0)
            change = data.get('change', 0)
            change_pct = data.get('change_percent', 0)
            
            print(f"{data.get('name')}")
            print(f"  Level:  {price:.2f}")
            print(f"  Change: {change:+.2f} ({change_pct:+.2f}%)")
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 2 completed")


async def example_3_get_historical_data():
    """
    Example 3: Get Historical Price Data
    
    Demonstrates retrieving historical OHLCV data for technical analysis.
    """
    print("\n" + "="*70)
    print("Example 3: Get Historical Price Data")
    print("="*70)
    
    builder = AbhikartaMCPServerProxy()
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
        
        tool = registry.get("yahoo_get_history:abhikartamcp")
        
        if not tool:
            print("❌ yahoo_get_history tool not found")
            return
        
        print(f"✓ Found tool: {tool.name}")
        
        # Example 3a: Get 1 year of daily data
        print("\n--- 1 Year Daily Data for AAPL ---")
        result = await tool.execute_async(
            symbol="AAPL",
            period="1y",
            interval="1d",
            include_events=True
        )
        
        if result:
            data = extract_data(result)
            print(f"Symbol: {data.get('symbol')}")
            print(f"Period: {data.get('period')}")
            print(f"Interval: {data.get('interval')}")
            print(f"Data points: {data.get('data_points')}")
            
            history = data.get('history', [])
            if history:
                print(f"\nFirst 5 days:")
                print(f"{'Date':<12} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<12}")
                print("-" * 72)
                
                for row in history[:5]:
                    date = row.get('date', '')[:10]
                    open_price = row.get('open', 0)
                    high = row.get('high', 0)
                    low = row.get('low', 0)
                    close = row.get('close', 0)
                    volume = row.get('volume', 0)
                    
                    print(f"{date:<12} ${open_price:<9.2f} ${high:<9.2f} ${low:<9.2f} ${close:<9.2f} {volume:<12,}")
                
                print(f"\nLast 5 days:")
                for row in history[-5:]:
                    date = row.get('date', '')[:10]
                    close = row.get('close', 0)
                    volume = row.get('volume', 0)
                    print(f"  {date}: ${close:.2f} (Vol: {volume:,})")
            
            # Show dividend and split events
            dividends = data.get('dividends', [])
            if dividends:
                print(f"\nDividend events ({len(dividends)}):")
                for div in dividends[:3]:
                    print(f"  {div.get('date')}: ${div.get('amount'):.2f}")
            
            splits = data.get('splits', [])
            if splits:
                print(f"\nStock splits ({len(splits)}):")
                for split in splits:
                    print(f"  {split.get('date')}: {split.get('ratio')}")
        
        # Example 3b: Get intraday data
        print("\n--- Intraday 5-Minute Data for TSLA ---")
        result = await tool.execute_async(
            symbol="TSLA",
            period="1d",
            interval="5m"
        )
        
        if result:
            data = extract_data(result)
            print(f"Symbol: {data.get('symbol')}")
            print(f"Intraday data points: {data.get('data_points')}")
            
            history = data.get('history', [])
            if history:
                print("\nFirst hour of trading:")
                for row in history[:12]:  # First 12 intervals = 1 hour
                    time = row.get('date', '')[11:16]  # Extract HH:MM
                    close = row.get('close', 0)
                    volume = row.get('volume', 0)
                    print(f"  {time}: ${close:.2f} (Vol: {volume:,})")
        
        # Example 3c: Get weekly data for long-term trend
        print("\n--- 5-Year Weekly Data for MSFT ---")
        result = await tool.execute_async(
            symbol="MSFT",
            period="5y",
            interval="1wk"
        )
        
        if result:
            data = extract_data(result)
            history = data.get('history', [])
            
            if history:
                print(f"Total weeks: {len(history)}")
                
                # Calculate simple price performance
                first_close = history[0].get('close', 0)
                last_close = history[-1].get('close', 0)
                
                if first_close and last_close:
                    performance = ((last_close - first_close) / first_close) * 100
                    
                    print(f"\nPrice Performance:")
                    print(f"  Start: ${first_close:.2f}")
                    print(f"  End:   ${last_close:.2f}")
                    print(f"  Change: {performance:+.2f}%")
        
        # Example 3d: Year-to-date data
        print("\n--- Year-to-Date Data for NVDA ---")
        result = await tool.execute_async(
            symbol="NVDA",
            period="ytd",
            interval="1d"
        )
        
        if result:
            data = extract_data(result)
            history = data.get('history', [])
            
            if history:
                print(f"YTD trading days: {len(history)}")
                
                # Find highs and lows
                closes = [row.get('close', 0) for row in history if row.get('close')]
                if closes:
                    ytd_high = max(closes)
                    ytd_low = min(closes)
                    current = closes[-1]
                    
                    print(f"\nYTD Performance:")
                    print(f"  High: ${ytd_high:.2f}")
                    print(f"  Low:  ${ytd_low:.2f}")
                    print(f"  Current: ${current:.2f}")
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 3 completed")


async def example_4_portfolio_monitoring():
    """
    Example 4: Portfolio Monitoring
    
    Complete workflow for monitoring a stock portfolio.
    """
    print("\n" + "="*70)
    print("Example 4: Portfolio Monitoring")
    print("="*70)
    
    # Define a sample portfolio
    portfolio = {
        "AAPL": {"shares": 50, "cost_basis": 150.00},
        "GOOGL": {"shares": 25, "cost_basis": 2500.00},
        "MSFT": {"shares": 40, "cost_basis": 300.00},
        "TSLA": {"shares": 15, "cost_basis": 700.00},
    }
    
    builder = AbhikartaMCPServerProxy()
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
        
        quote_tool = registry.get("yahoo_get_quote:abhikartamcp")
        
        if not quote_tool:
            print("❌ yahoo_get_quote tool not found")
            return
        
        print("\n📊 Portfolio Analysis")
        print("="*70)
        
        total_cost = 0
        total_value = 0
        portfolio_data = []
        
        for symbol, position in portfolio.items():
            shares = position['shares']
            cost_basis = position['cost_basis']
            
            # Get current quote
            result = await quote_tool.execute_async(symbol=symbol)
            
            if result:
                data = extract_data(result)
                current_price = data.get('price', 0)
                
                # Calculate metrics
                cost = shares * cost_basis
                value = shares * current_price
                gain_loss = value - cost
                gain_loss_pct = (gain_loss / cost) * 100 if cost else 0
                
                total_cost += cost
                total_value += value
                
                portfolio_data.append({
                    'symbol': symbol,
                    'name': data.get('name', symbol),
                    'shares': shares,
                    'cost_basis': cost_basis,
                    'current_price': current_price,
                    'cost': cost,
                    'value': value,
                    'gain_loss': gain_loss,
                    'gain_loss_pct': gain_loss_pct
                })
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Display portfolio summary
        print(f"\n{'Symbol':<8} {'Shares':<8} {'Cost':<12} {'Value':<12} {'Gain/Loss':<15} {'%':<10}")
        print("-" * 75)
        
        for stock in portfolio_data:
            gain_loss_str = f"${stock['gain_loss']:+,.2f}"
            pct_str = f"{stock['gain_loss_pct']:+.2f}%"
            
            print(f"{stock['symbol']:<8} {stock['shares']:<8} "
                  f"${stock['cost']:<11,.2f} ${stock['value']:<11,.2f} "
                  f"{gain_loss_str:<15} {pct_str:<10}")
        
        # Portfolio totals
        total_gain_loss = total_value - total_cost
        total_gain_loss_pct = (total_gain_loss / total_cost) * 100 if total_cost else 0
        
        print("=" * 75)
        print(f"{'TOTAL':<8} {'':<8} ${total_cost:<11,.2f} ${total_value:<11,.2f} "
              f"${total_gain_loss:+,.2f}      {total_gain_loss_pct:+.2f}%")
        
        print(f"\n{'='*70}")
        print(f"Portfolio Summary:")
        print(f"  Total Investment: ${total_cost:,.2f}")
        print(f"  Current Value:    ${total_value:,.2f}")
        print(f"  Total Return:     ${total_gain_loss:+,.2f} ({total_gain_loss_pct:+.2f}%)")
        print(f"{'='*70}")
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 4 completed")


async def example_5_market_research():
    """
    Example 5: Market Research Workflow
    
    Complete market research workflow: search, analyze, and compare.
    """
    print("\n" + "="*70)
    print("Example 5: Market Research Workflow")
    print("="*70)
    
    builder = AbhikartaMCPServerProxy()
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
        
        search_tool = registry.get("yahoo_search_symbols:abhikartamcp")
        quote_tool = registry.get("yahoo_get_quote:abhikartamcp")
        history_tool = registry.get("yahoo_get_history:abhikartamcp")
        
        # Step 1: Search for companies in a sector
        print("\nStep 1: Search for Semiconductor Companies")
        print("-" * 50)
        
        if search_tool:
            result = await search_tool.execute_async(
                query="semiconductor",
                limit=10
            )
            
            if result:
                data = extract_data(result)
                companies = data.get('results', [])
                
                if companies:
                    print(f"✓ Found {len(companies)} semiconductor companies")
                    
                    # Pick top 3 for analysis
                    top_companies = companies[:3]
                    symbols = [c.get('symbol') for c in top_companies]
                    
                    for company in top_companies:
                        print(f"  • {company.get('name')} ({company.get('symbol')})")
        
        # Step 2: Get current quotes for comparison
        print("\nStep 2: Compare Current Valuations")
        print("-" * 50)
        
        if quote_tool and symbols:
            print(f"\n{'Symbol':<8} {'Price':<12} {'Market Cap':<15} {'P/E':<8}")
            print("-" * 50)
            
            for symbol in symbols:
                result = await quote_tool.execute_async(symbol=symbol)
                
                if result:
                    data = extract_data(result)
                    price = data.get('price', 0)
                    market_cap = data.get('market_cap', 0)
                    pe = data.get('pe_ratio', 0)
                    
                    mc_str = f"${market_cap/1e9:.1f}B" if market_cap else "N/A"
                    pe_str = f"{pe:.1f}" if pe else "N/A"
                    
                    print(f"{symbol:<8} ${price:<11.2f} {mc_str:<15} {pe_str:<8}")
                
                await asyncio.sleep(0.5)
        
        # Step 3: Analyze historical performance
        print("\nStep 3: Analyze 6-Month Performance")
        print("-" * 50)
        
        if history_tool and symbols:
            for symbol in symbols:
                result = await history_tool.execute_async(
                    symbol=symbol,
                    period="6mo",
                    interval="1d"
                )
                
                if result:
                    data = extract_data(result)
                    history = data.get('history', [])
                    
                    if history and len(history) > 1:
                        start_price = history[0].get('close', 0)
                        end_price = history[-1].get('close', 0)
                        
                        if start_price and end_price:
                            performance = ((end_price - start_price) / start_price) * 100
                            
                            print(f"\n{symbol}:")
                            print(f"  6-Month Return: {performance:+.2f}%")
                            print(f"  Start: ${start_price:.2f}")
                            print(f"  End:   ${end_price:.2f}")
                
                await asyncio.sleep(0.5)
        
        print("\n" + "="*70)
        print("Research Workflow Summary:")
        print("  1. Searched for sector companies ✓")
        print("  2. Compared current valuations ✓")
        print("  3. Analyzed historical performance ✓")
        print("="*70)
        
    finally:
        await builder.stop()
    
    print("\n✓ Example 5 completed")


async def main():
    """Run all Yahoo Finance examples"""
    
    print("="*70)
    print("ABHIKARTA MCP INTEGRATION - YAHOO FINANCE TOOLS EXAMPLES")
    print("Copyright © 2025-2030, Ashutosh Sinha (ajsinha@gmail.com)")
    print("="*70)
    
    try:
        # Run all examples
        await example_1_search_symbols()
        await example_2_get_stock_quotes()
        await example_3_get_historical_data()
        await example_4_portfolio_monitoring()
        await example_5_market_research()
        
        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
