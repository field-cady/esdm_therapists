#!/usr/bin/env python3
"""
Uses browser-use with an LLM to scrape the ESDM therapists table
using natural language instructions.
"""

import asyncio
import csv
from langchain_openai import ChatOpenAI
from browser_use_sdk import Agent


async def scrape_with_browser_use():
    """
    Use browser-use to navigate to the ESDM website and extract the therapist table.
    """
    
    # Initialize the LLM with OpenAI
    llm = ChatOpenAI(
        model="gpt-4o",
        timeout=300,
    )
    
    # Create the agent with natural language task
    agent = Agent(
        task="""
        Go to the website https://www.esdm.co/esdm-therapists
        
        Wait for the page to fully load and for the therapist table to appear.
        
        Find the table containing therapist information. Extract ALL data from this table,
        including all column headers and all rows.
        
        Return the data in a structured format where I can access:
        - headers: a list of column names
        - rows: a list of lists, where each inner list is a row of data
        """,
        llm=llm,
    )
    
    print("Starting browser automation with natural language instructions...")
    print("This may take a minute or two...\n")
    
    # Run the agent
    result = await agent.run()
    
    return result


def parse_result_to_table(result):
    """
    Parse the agent result and extract table data.
    The exact format depends on how browser-use returns the data.
    """
    # browser-use typically returns results in result.final_result() or similar
    # You may need to adjust this based on the actual return format
    
    # For now, return the raw result for inspection
    return result


async def main():
    try:
        # Get the data using browser-use
        result = await scrape_with_browser_use()
        
        print("\n" + "="*60)
        print("RESULT FROM BROWSER-USE:")
        print("="*60)
        print(result)
        print("="*60 + "\n")
        
        # TODO: Parse the result and save to TSV
        # The exact parsing will depend on the format returned by browser-use
        # You'll likely need to inspect the result object first
        
        print("\nTo save as TSV, inspect the result structure above and update the script.")
        print("The data might be in result.final_result(), result.extracted_content, or similar.")
        
        # Example of how to save once you know the structure:
        
        if hasattr(result, 'headers') and hasattr(result, 'rows'):
            with open('scred_data.tsv', 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter='\\t')
                writer.writerow(result.headers)
                writer.writerows(result.rows)
            print("Saved to scred_data.tsv")
        
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())