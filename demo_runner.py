#!/usr/bin/env python3
"""
Gambling Unifier - Demo Runner
Simple demonstration of the system capabilities using sample data
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def load_sample_data():
    """Load the sample data files"""
    sample_dir = Path('sample_outputs')
    
    if not sample_dir.exists():
        print("❌ Sample outputs not found! Run sample_demo.py first.")
        return None
    
    try:
        # Load raw products
        with open(sample_dir / 'raw_products.json', 'r') as f:
            raw_products = json.load(f)
        
        # Load unified products
        with open(sample_dir / 'unified_products.csv', 'r') as f:
            reader = csv.DictReader(f)
            unified_products = list(reader)
        
        # Load analysis report
        with open(sample_dir / 'analysis_report.md', 'r') as f:
            analysis_report = f.read()
        
        # Load RAG examples
        with open(sample_dir / 'rag_qa_examples.json', 'r') as f:
            rag_examples = json.load(f)
            
        return {
            'raw_products': raw_products,
            'unified_products': unified_products,
            'analysis_report': analysis_report,
            'rag_examples': rag_examples
        }
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return None

def demonstrate_data_collection(data):
    """Demonstrate the data collection phase"""
    print("\n🔍 PHASE 1: DATA COLLECTION")
    print("=" * 40)
    
    raw_products = data['raw_products']
    total_products = sum(len(products) for products in raw_products.values())
    
    print(f"✅ Successfully collected data from {len(raw_products)} platforms")
    print(f"📊 Total products collected: {total_products}")
    
    for platform, products in raw_products.items():
        print(f"\n📡 {platform.upper()}:")
        for product in products:
            print(f"   • {product['name']}")
            print(f"     💰 Price: ${product['price']:.2f}")
            print(f"     🆔 ID: {product['product_id']}")

def demonstrate_unification(data):
    """Demonstrate the product unification phase"""
    print("\n🔗 PHASE 2: PRODUCT UNIFICATION")
    print("=" * 40)
    
    unified_products = data['unified_products']
    
    print(f"✅ Successfully unified {len(unified_products)} products")
    
    # Group by confidence levels
    high_confidence = [p for p in unified_products if float(p['confidence']) >= 0.95]
    good_confidence = [p for p in unified_products if 0.89 <= float(p['confidence']) < 0.95]
    
    print(f"\n🎯 High Confidence Matches (95%+): {len(high_confidence)}")
    for product in high_confidence[:2]:
        print(f"   • {product['name']}")
        print(f"     📍 Sites: {product['matched_sites']}")
        print(f"     🎯 Confidence: {product['confidence']}%")
    
    print(f"\n✅ Good Confidence Matches (89-94%): {len(good_confidence)}")
    for product in good_confidence[:2]:
        print(f"   • {product['name']}")
        print(f"     📍 Sites: {product['matched_sites']}")
        print(f"     🎯 Confidence: {product['confidence']}%")

def demonstrate_analysis(data):
    """Demonstrate the analysis capabilities"""
    print("\n📊 PHASE 3: MARKET ANALYSIS")
    print("=" * 40)
    
    unified_products = data['unified_products']
    
    # Calculate arbitrage opportunities
    arbitrage_opportunities = []
    product_groups = {}
    
    for product in unified_products:
        name = product['name']
        if name not in product_groups:
            product_groups[name] = []
        product_groups[name].append(product)
    
    for name, products in product_groups.items():
        if len(products) > 1:
            prices = [float(p['price']) for p in products]
            min_price = min(prices)
            max_price = max(prices)
            spread = ((max_price - min_price) / min_price) * 100
            
            if spread > 5:  # 5% threshold
                arbitrage_opportunities.append({
                    'name': name,
                    'spread': spread,
                    'min_price': min_price,
                    'max_price': max_price
                })
    
    print(f"💰 Arbitrage Opportunities Found: {len(arbitrage_opportunities)}")
    
    for opp in arbitrage_opportunities:
        print(f"\n   📈 {opp['name']}")
        print(f"      💸 Price Spread: {opp['spread']:.1f}%")
        print(f"      📉 Min Price: ${opp['min_price']:.2f}")
        print(f"      📈 Max Price: ${opp['max_price']:.2f}")
        print(f"      💰 Potential Profit: ${opp['max_price'] - opp['min_price']:.2f}")

def demonstrate_rag_capabilities(data):
    """Demonstrate the RAG system capabilities"""
    print("\n🤖 PHASE 4: RAG INTELLIGENCE")
    print("=" * 40)
    
    rag_examples = data['rag_examples']
    
    print(f"✅ RAG system ready with {len(rag_examples)} sample Q&A pairs")
    
    for i, qa in enumerate(rag_examples, 1):
        print(f"\n❓ Question {i}: {qa['question']}")
        answer_preview = qa['answer'][:150] + "..." if len(qa['answer']) > 150 else qa['answer']
        print(f"🤖 Answer {i}: {answer_preview}")

def run_demo():
    """Run the complete demonstration"""
    print("🎰 GAMBLING UNIFIER - SYSTEM DEMONSTRATION")
    print("=" * 50)
    print("This demo shows the complete workflow using sample data")
    print("No API calls or web scraping required!")
    
    # Load sample data
    data = load_sample_data()
    if not data:
        return
    
    print("\n🚀 Starting system demonstration...")
    
    # Run through all phases
    demonstrate_data_collection(data)
    demonstrate_unification(data)
    demonstrate_analysis(data)
    demonstrate_rag_capabilities(data)
    
    print("\n" + "=" * 50)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 50)
    print("✅ Data Collection: Successfully demonstrated")
    print("✅ Product Unification: High confidence matching achieved")
    print("✅ Market Analysis: Arbitrage opportunities identified")
    print("✅ RAG Intelligence: AI-powered insights generated")
    
    print("\n📁 All sample data available in: sample_outputs/")
    print("🚀 System ready for real-world deployment!")

if __name__ == "__main__":
    run_demo()
