"""
E-commerce Intelligence Platform Demo using Graphiti-Cosmos
===========================================================

This demo showcases how Graphiti-Cosmos can power an advanced e-commerce intelligence 
platform that transforms business events into actionable insights through temporal 
knowledge graphs.

Use Case: Manybirds E-commerce Intelligence
- Product catalog intelligence
- Customer behavior tracking
- Purchase pattern analysis
- Recommendation engine
- Market trend detection
- Supplier relationship mapping
"""

import asyncio
import json
import os
import platform
import random
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the src directory to the path so we can import graphiti_cosmos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graphiti_cosmos import GraphitiCosmos, Episode, GraphitiCosmosConfig

# Fix for Windows ProactorEventLoop issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class EcommerceIntelligenceDemo:
    """Demo of e-commerce intelligence using Graphiti-Cosmos"""
    
    def __init__(self):
        self.graphiti = None
        self.customers = []
        self.products = []
        
    async def initialize(self):
        """Initialize the system"""
        print("🏪 Initializing E-commerce Intelligence Platform...")
        self.graphiti = GraphitiCosmos()
        await self.graphiti.initialize()
        # Monkey-patch entity creation to sanitize names invalid for Cosmos DB ids
        original_create_or_update = self.graphiti._create_or_update_entity
        async def _sanitize_create_or_update(entity, episode_id):
            # replace invalid id characters
            entity.name = entity.name.replace('/', '_').replace('\\', '_')
            return await original_create_or_update(entity, episode_id)
        self.graphiti._create_or_update_entity = _sanitize_create_or_update
        print("✅ Platform ready!")
        # Load product data
        await self.load_product_catalog()
        
    async def cleanup(self):
        """Clean up connections properly"""
        if self.graphiti:
            try:
                await self.graphiti.close()
                print("🔌 Disconnected from Graphiti-Cosmos")
            except Exception as e:
                print(f"⚠️  Warning during cleanup: {e}")
                # Silently handle cleanup errors

    async def load_product_catalog(self):
        """Load Manybirds product catalog"""
        try:
            with open("manybirds_products.json", "r") as f:
                data = json.load(f)
                # Extract the products array from the JSON structure
                if isinstance(data, dict) and "products" in data:
                    raw_products = data["products"]
                elif isinstance(data, list):
                    raw_products = data
                else:
                    raw_products = []
                
                # Normalize product data to expected format
                self.products = self.normalize_products(raw_products)
            print(f"📦 Loaded {len(self.products)} products from catalog")
        except FileNotFoundError:            # Create sample products if file doesn't exist
            self.products = self.generate_sample_products()
            print(f"📦 Generated {len(self.products)} sample products")
    
    def normalize_products(self, raw_products):
        """Normalize product data from Manybirds JSON to expected format"""
        normalized = []
        for product in raw_products:
            # Extract price from variants if available
            price = 99.99  # default price
            if "variants" in product and product["variants"]:
                try:
                    price = float(product["variants"][0].get("price", 99.99))
                except (ValueError, KeyError, IndexError):
                    price = 99.99
              # Sanitize product ID by removing invalid characters for Cosmos DB Graph
            raw_id = str(product.get("id", f"PROD_{len(normalized)+1:03d}"))
            sanitized_id = self.sanitize_id(raw_id)
            
            normalized_product = {
                "id": sanitized_id,
                "name": product.get("title", f"Product {len(normalized)+1}"),
                "category": product.get("product_type", "General"),
                "price": price,
                "description": product.get("body_html", "Premium product with excellent features"),
                "brand": product.get("vendor", "Manybirds"),
                "rating": round(random.uniform(3.5, 5.0), 1)  # Generate rating since not in data
            }
            normalized.append(normalized_product)
        
        return normalized
    
    def generate_sample_products(self):
        """Generate sample products if catalog not available"""
        categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books"]
        products = []
        
        for i in range(20):
            products.append({
                "id": f"PROD_{i+1:03d}",
                "name": f"Premium Product {i+1}",
                "category": random.choice(categories),
                "price": round(random.uniform(19.99, 299.99), 2),
                "description": f"High-quality product {i+1} with excellent features",
                "brand": f"Brand{random.randint(1,5)}",
                "rating": round(random.uniform(3.5, 5.0), 1)
            })
        return products
    
    async def simulate_customer_journey(self, customer_name: str, journey_type: str = "exploration"):
        """Simulate a customer journey through the platform"""
        print(f"\n👤 Simulating customer journey for {customer_name} ({journey_type})")
          # Generate timestamp for this session
        base_time = datetime.now() - timedelta(days=random.randint(0, 30))
        raw_session_id = f"session_{customer_name.replace(' ', '_')}_{int(time.time())}"
        session_id = self.sanitize_id(raw_session_id)
        
        if journey_type == "exploration":
            await self._simulate_exploration_journey(customer_name, session_id, base_time)
        elif journey_type == "purchase":
            await self._simulate_purchase_journey(customer_name, session_id, base_time)
        elif journey_type == "return_customer":
            await self._simulate_return_customer_journey(customer_name, session_id, base_time)
    
    async def _simulate_exploration_journey(self, customer_name, session_id, base_time):
        """Simulate customer exploring products"""
        # Browse categories
        category = random.choice(["Electronics", "Clothing", "Home & Garden"])
        content = f"{customer_name} browsed the {category} category on Manybirds. They spent time exploring different product options and reading reviews."
        episode_id = self.sanitize_id(f"browse_{session_id}_category")
        episode = Episode(
            content=content,
            episode_id=episode_id
        )
        await self.graphiti.add_episode(episode)
        
        # View specific products
        viewed_products = random.sample(self.products, min(3, len(self.products)))
        for product in viewed_products:
            content = f"{customer_name} viewed {product['name']} priced at ${product['price']} in the {product['category']} category. They read the product description and checked the rating of {product.get('rating', 4.0)} stars."
            episode_id = self.sanitize_id(f"view_{session_id}_{product['id']}")
            episode = Episode(
                content=content,
                episode_id=episode_id
            )
            await self.graphiti.add_episode(episode)
        
        print(f"  📱 {customer_name} explored {category} category and viewed {len(viewed_products)} products")
    
    async def _simulate_purchase_journey(self, customer_name, session_id, base_time):
        """Simulate customer making a purchase"""
        # Select product to purchase
        product = random.choice(self.products)
        # Add to cart
        content = f"{customer_name} added {product['name']} to their shopping cart. The product costs ${product['price']} and belongs to the {product['category']} category."
        episode_id = self.sanitize_id(f"cart_{session_id}_{product['id']}")
        episode = Episode(
            content=content,
            episode_id=episode_id
        )
        await self.graphiti.add_episode(episode)
        # Complete purchase
        content = f"{customer_name} completed purchase of {product['name']} for ${product['price']}. The transaction was successful and the customer received a confirmation email. The order will be shipped within 2-3 business days."
        episode_id = self.sanitize_id(f"purchase_{session_id}_{product['id']}")
        episode = Episode(
            content=content,
            episode_id=episode_id
        )
        await self.graphiti.add_episode(episode)
        # Post-purchase interaction
        content = f"{customer_name} received their order confirmation for {product['name']}. They signed up for delivery notifications and expressed satisfaction with the purchase process."
        episode_id = self.sanitize_id(f"confirmation_{session_id}_{product['id']}")
        episode = Episode(
            content=content,
            episode_id=episode_id
        )
        await self.graphiti.add_episode(episode)
        
        print(f"  💳 {customer_name} purchased {product['name']} for ${product['price']}")
    
    async def _simulate_return_customer_journey(self, customer_name, session_id, base_time):
        """Simulate returning customer with personalized experience"""
        # Check previous purchases (simulated)
        content = f"{customer_name} returned to Manybirds platform. The system recognized them as a returning customer and showed personalized recommendations based on their previous purchase history."
        episode_id = self.sanitize_id(f"return_{session_id}_recognition")
        episode = Episode(
            content=content,
            episode_id=episode_id
        )
        await self.graphiti.add_episode(episode)
        
        # View recommendations
        recommended_products = random.sample(self.products, 2)
        for product in recommended_products:
            content = f"{customer_name} viewed recommended product {product['name']} which was suggested based on their purchase history and preferences. The recommendation algorithm identified this as a high-interest item."
            episode_id = self.sanitize_id(f"recommendation_{session_id}_{product['id']}")
            episode = Episode(
                content=content,
                episode_id=episode_id
            )
            await self.graphiti.add_episode(episode)
        
        print(f"  🔄 {customer_name} returned and viewed {len(recommended_products)} personalized recommendations")
    
    async def analyze_customer_insights(self):
        """Analyze customer behavior patterns"""
        print("\n📊 CUSTOMER INSIGHTS ANALYSIS")
        print("=" * 50)
        
        # Search for purchase patterns
        purchase_results = await self.graphiti.search_relationships("purchase")
        print(f"🛒 Purchase Events: {len(purchase_results)}")
        
        # Search for browsing patterns
        browse_results = await self.graphiti.search_relationships("browsed")
        print(f"👀 Browse Events: {len(browse_results)}")
        
        # Search for product views
        view_results = await self.graphiti.search_relationships("viewed")
        print(f"📱 Product Views: {len(view_results)}")
        
        # Analyze popular products
        product_entities = await self.graphiti.search_entities("Product")
        print(f"📦 Products in Graph: {len(product_entities)}")
        
        # Show some example insights
        if purchase_results:
            print(f"\n💡 Sample Purchase Insight:")
            purchase = purchase_results[0]
            print(f"   Customer: {purchase['source']}")
            print(f"   Product: {purchase['target']}")
            print(f"   Relationship: {purchase['relationship']}")
    
    async def generate_recommendations(self, customer_name: str):
        """Generate product recommendations for a customer"""
        print(f"\n🎯 GENERATING RECOMMENDATIONS FOR {customer_name}")
        print("=" * 50)
        
        # Search for customer by different methods
        # Try exact match first
        customer_results = await self.graphiti.search_entities(customer_name)
        
        # If no exact match, try searching for "customer" type and filter
        if not customer_results:
            all_customers = await self.graphiti.search_entities("customer")
            customer_results = [c for c in all_customers if customer_name.lower() in str(c).lower()]
        
        # Also try searching in relationships
        if not customer_results:
            customer_relationships = await self.graphiti.search_relationships(customer_name)
            if customer_relationships:
                customer_results = [{"name": customer_name, "found_in": "relationships"}]
        
        # Try searching for person entities (since customers might be stored as person type)
        if not customer_results:
            person_results = await self.graphiti.search_entities("person")
            customer_results = [p for p in person_results if customer_name.lower() in str(p).lower()]
        
        # Also try with sanitized name (in case spaces were replaced)
        if not customer_results:
            sanitized_name = customer_name.replace(" ", "_")
            customer_results = await self.graphiti.search_entities(sanitized_name)
        if customer_results:
            print(f"✅ Found customer profile for {customer_name}")
            print(f"   Profile data: {customer_results[0] if customer_results else 'No data'}")
            
            # Get customer's connected products using different search methods
            neighbors = []
            try:
                # Search for relationships where customer is mentioned
                customer_rels = await self.graphiti.search_relationships(customer_name)
                if customer_rels:
                    neighbors = customer_rels
                    
                # Also try with sanitized customer name
                sanitized_customer = customer_name.replace(" ", "_")
                customer_rels_sanitized = await self.graphiti.search_relationships(sanitized_customer)
                if customer_rels_sanitized:
                    neighbors.extend(customer_rels_sanitized)
                    
            except Exception as e:
                print(f"⚠️  Error getting customer relationships: {e}")
                neighbors = []
            
            print(f"🔗 Customer connections: {len(neighbors)} items")
            
            # Show neighbor connections (these represent purchase/view history)
            if neighbors and isinstance(neighbors, list):
                print("📋 Customer's interaction history:")
                # Safely iterate through neighbors list
                display_neighbors = neighbors[:5] if len(neighbors) > 5 else neighbors
                for i, neighbor in enumerate(display_neighbors, 1):
                    if isinstance(neighbor, dict):
                        target = neighbor.get('target', neighbor.get('name', 'Unknown'))
                        rel_type = neighbor.get('relationship', neighbor.get('type', 'interaction'))
                        print(f"   {i}. {target} ({rel_type})")
                    else:
                        print(f"   {i}. {neighbor}")
            elif neighbors:
                print("📋 Customer's interaction history:")
                print(f"   Found {len(neighbors)} connections (complex format)")
            
            # Simulate recommendation logic
            print(f"\n💡 Recommended products for {customer_name}:")
            # In a real system, this would use collaborative filtering, content-based filtering, etc.
            recommended = random.sample(self.products, 3)
            for i, product in enumerate(recommended, 1):
                print(f"   {i}. {product['name']} (${product['price']}) - {product['category']}")
                print(f"      Reason: Based on similar customer preferences")
        else:
            print(f"❌ No profile found for {customer_name}")
            print("💡 Showing popular products instead:")
            popular = random.sample(self.products, 3)
            for i, product in enumerate(popular, 1):
                print(f"   {i}. {product['name']} (${product['price']}) - {product['category']}")
    
    async def market_trend_analysis(self):
        """Analyze market trends from the knowledge graph"""
        print("\n📈 MARKET TREND ANALYSIS")
        print("=" * 50)
        
        # Get overall graph statistics
        stats = await self.graphiti.get_graph_stats()
        print(f"📊 Graph Overview:")
        print(f"   Episodes: {stats['episodes']}")
        print(f"   Entities: {stats['entities']}")
        print(f"   Relationships: {stats['relationships']}")
        
        # Analyze popular categories
        category_results = await self.graphiti.search_entities("category")
        print(f"\n🏷️  Product Categories: {len(category_results)} found")
        
        # Analyze customer engagement
        customer_results = await self.graphiti.search_entities("customer")
        print(f"👥 Active Customers: {len(customer_results)} found")
        
        # Show trending patterns
        trending_relationships = await self.graphiti.search_relationships("added")
        print(f"🔥 Cart Additions: {len(trending_relationships)} events")
        
        # Simulate insights
        print(f"\n💡 Key Insights:")
        print(f"   • Customer engagement is growing with {stats['episodes']} total interactions")
        print(f"   • Average {stats['relationships']/max(stats['episodes'], 1):.1f} actions per customer session")
        print(f"   • Knowledge graph captures {stats['entities']} unique business entities")
    
    async def generate_intelligence_reports(self):
        """Generate and save intelligence reports to a dedicated folder"""
        import os
        
        print("\n📋 GENERATING INTELLIGENCE REPORTS")
        print("-" * 40)
        
        # Create reports directory if it doesn't exist
        reports_dir = "ecommerce_intelligence_reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Customer insights report
        customer_report = [
            "===== CUSTOMER INSIGHTS REPORT =====",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "CUSTOMER BEHAVIOR ANALYSIS:",
        ]
        
        # Get customer data
        purchase_results = await self.graphiti.search_relationships("purchase")
        browse_results = await self.graphiti.search_relationships("browsed")
        view_results = await self.graphiti.search_relationships("viewed")
        
        customer_report.append(f"• Purchase Events: {len(purchase_results)}")
        customer_report.append(f"• Browse Events: {len(browse_results)}")
        customer_report.append(f"• Product View Events: {len(view_results)}\n")
        
        customer_report.append("CUSTOMER INSIGHTS:")
        if purchase_results:
            for i, purchase in enumerate(purchase_results[:5], 1):
                customer_report.append(f"  Purchase {i}: Customer {purchase['source']} purchased {purchase['target']}")
        
        # Save customer report
        customer_report_path = os.path.join(reports_dir, f"customer_insights_{current_time}.txt")
        with open(customer_report_path, "w") as f:
            f.write("\n".join(customer_report))
        
        # 2. Product insights report
        product_report = [
            "===== PRODUCT INSIGHTS REPORT =====",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "PRODUCT CATALOG ANALYSIS:",
        ]
        
        product_entities = await self.graphiti.search_entities("Product")
        product_report.append(f"• Total Products: {len(product_entities)}")
        
        # Get some product details
        product_report.append("\nPOPULAR PRODUCTS:")
        products = random.sample(self.products, min(5, len(self.products)))
        for i, product in enumerate(products, 1):
            product_report.append(f"  {i}. {product['name']} (${product['price']}) - {product['category']}")
        
        # Save product report
        product_report_path = os.path.join(reports_dir, f"product_insights_{current_time}.txt")
        with open(product_report_path, "w") as f:
            f.write("\n".join(product_report))
        
        # 3. Market trends report
        market_report = [
            "===== MARKET TRENDS REPORT =====",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "MARKET ANALYSIS:",
        ]
        
        # Get graph stats
        stats = await self.graphiti.get_graph_stats()
        market_report.append(f"• Total Business Events: {stats['episodes']}")
        market_report.append(f"• Business Entities: {stats['entities']}")
        market_report.append(f"• Relationships Mapped: {stats['relationships']}")
        market_report.append(f"• Intelligence Density: {stats['relationships']/max(stats['entities'], 1):.2f} connections per entity\n")
        
        # Add category analysis
        category_results = await self.graphiti.search_entities("category")
        market_report.append(f"• Product Categories: {len(category_results)} found")
        
        # Add trending analysis
        market_report.append("\nKEY MARKET INSIGHTS:")
        market_report.append("• Customer engagement is growing with increasing interaction counts")
        market_report.append(f"• Average {stats['relationships']/max(stats['episodes'], 1):.1f} actions per customer session")
        market_report.append("• Online shopping activity shows strong category-specific patterns")
        
        # Save market report
        market_report_path = os.path.join(reports_dir, f"market_trends_{current_time}.txt")
        with open(market_report_path, "w") as f:
            f.write("\n".join(market_report))
        
        # 4. Business intelligence summary
        summary_report = [
            "===== BUSINESS INTELLIGENCE SUMMARY =====",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "KNOWLEDGE GRAPH METRICS:",
        ]
        
        summary_report.append(f"• Episodes Processed: {stats['episodes']}")
        summary_report.append(f"• Entities Identified: {stats['entities']}")
        summary_report.append(f"• Relationships Mapped: {stats['relationships']}")
        summary_report.append(f"• Intelligence Density: {stats['relationships']/max(stats['entities'], 1):.2f}\n")
        
        summary_report.append("ACTION RECOMMENDATIONS:")
        summary_report.append("• Focus marketing on highest-engaging product categories")
        summary_report.append("• Optimize product pages for most-viewed items")
        summary_report.append("• Develop personalized recommendations based on browsing patterns")
        summary_report.append("• Enhance checkout experience to improve conversion rates")
        
        # Save summary report
        summary_report_path = os.path.join(reports_dir, f"business_summary_{current_time}.txt")
        with open(summary_report_path, "w") as f:
            f.write("\n".join(summary_report))
        
        print(f"✅ Generated 4 intelligence reports in '{reports_dir}' folder:")
        print(f"  • Customer Insights")
        print(f"  • Product Intelligence")
        print(f"  • Market Trends")
        print(f"  • Business Summary")
    
    async def run_full_demo(self):
        """Run the complete e-commerce intelligence demo"""
        print("🏪 MANYBIRDS E-COMMERCE INTELLIGENCE PLATFORM")
        print("=" * 60)
        print("Demonstrating how Graphiti-Cosmos transforms business events")
        print("into actionable intelligence for e-commerce operations.")
        print("=" * 60)
        
        try:
            await self.initialize()
            
            # Simulate different customer journeys
            customers = [
                ("Sarah Johnson", "exploration"),
                ("Mike Chen", "purchase"),
                ("Emily Davis", "return_customer"),
                ("Alex Rodriguez", "purchase"),
                ("Jennifer Kim", "exploration")
            ]
            
            print(f"\n🎬 SIMULATING CUSTOMER JOURNEYS")
            print("-" * 40)
            
            for customer_name, journey_type in customers:
                await self.simulate_customer_journey(customer_name, journey_type)
                await asyncio.sleep(0.5)  # Small delay between simulations
            
            # Analysis phase
            print(f"\n🧠 INTELLIGENCE ANALYSIS PHASE")
            print("-" * 40)
            await self.analyze_customer_insights()
            await self.generate_recommendations("Sarah Johnson")
            await self.market_trend_analysis()
            
            # Generate intelligence reports
            await self.generate_intelligence_reports()
            
            # Show final statistics
            final_stats = await self.graphiti.get_graph_stats()
            print(f"\n🎯 FINAL PLATFORM STATISTICS")
            print("-" * 40)
            print(f"📈 Total Business Events Processed: {final_stats['episodes']}")
            print(f"🎯 Business Entities Identified: {final_stats['entities']}")
            print(f"🔗 Relationships Mapped: {final_stats['relationships']}")
            print(f"📊 Intelligence Density: {final_stats['relationships']/max(final_stats['entities'], 1):.2f} connections per entity")
            
            print(f"\n✅ DEMO COMPLETE!")
            print("🎉 Graphiti-Cosmos successfully transformed raw business events")
            print("   into a rich knowledge graph for e-commerce intelligence!")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()

    def sanitize_id(self, id_value):
        """Sanitize any ID to ensure it's compatible with Cosmos DB Graph"""
        if id_value is None:
            return "unknown_id"
        
        # Sanitize ID by removing invalid characters for Cosmos DB Graph
        sanitized = str(id_value).replace("/", "_").replace("\\", "_").replace(" ", "_").replace("-", "_")
        return sanitized

async def main():
    """Run the e-commerce intelligence demo"""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    demo = EcommerceIntelligenceDemo()
    try:
        await demo.run_full_demo()
    finally:
        # Add a small delay before Python exits to allow cleanup
        await asyncio.sleep(0.2)

if __name__ == "__main__":
    # Use asyncio.run which handles cleanup better
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
