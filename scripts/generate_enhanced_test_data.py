import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class EnhancedManybirdsDataGenerator:
    def __init__(self):
        self.product_types = [
            "Shoes", "Socks", "Accessories", "Apparel", "Bags", "Insoles", 
            "Laces", "Care Products", "Gift Cards", "Underwear"
        ]
        
        self.materials = [
            "wool", "cotton", "eucalyptus", "merino", "bamboo", "recycled", 
            "organic cotton", "tencel", "hemp", "linen", "alpaca", "cashmere"
        ]
        
        self.colors = [
            "black", "white", "grey", "beige", "brown", "navy", "green", "blue",
            "coral", "mint", "olive", "charcoal", "cream", "sage", "rust", "teal",
            "burgundy", "forest", "stone", "sand", "lavender", "rose"
        ]
        
        self.silhouettes = [
            "runner", "loafer", "slip-on", "high-top", "boot", "sandal", 
            "sneaker", "mule", "oxford", "derby", "chelsea", "ankle boot",
            "slide", "flip-flop", "mary jane", "ballet flat"
        ]
        
        self.genders = ["men", "women", "unisex", "kids", "toddler", "baby"]
        self.editions = ["classic", "limited", "seasonal", "core", "signature", "collaboration"]
        self.price_tiers = ["tier-1", "tier-2", "tier-3", "premium", "luxury"]
        
        # Expanded size options
        self.sizes = {
            "men": ["6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "12.5", "13", "14"],
            "women": ["4", "4.5", "5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5"],
            "kids": ["10.5", "11", "11.5", "12", "12.5", "13", "13.5", "1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5", "5.5", "6", "6.5", "7"],
            "toddler": ["2T", "3T", "4T", "5T", "6T", "7T", "8T", "9T", "10T", "11T", "12T"],
            "baby": ["0-3M", "3-6M", "6-9M", "9-12M", "12-18M", "18-24M"],
            "socks": ["XS", "S", "M", "L", "XL", "XXL"],
            "apparel": ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"],
            "accessories": ["One Size", "Small", "Medium", "Large"],
            "bags": ["One Size"],
            "insoles": ["6", "7", "8", "9", "10", "11", "12"]
        }
        
        # Enhanced pricing by category
        self.base_prices = {
            "shoes": {"min": 75, "max": 285},
            "socks": {"min": 8, "max": 32},
            "accessories": {"min": 15, "max": 125},
            "apparel": {"min": 35, "max": 195},
            "bags": {"min": 45, "max": 165},
            "insoles": {"min": 18, "max": 35},
            "laces": {"min": 8, "max": 18},
            "care products": {"min": 12, "max": 28},
            "gift cards": {"min": 25, "max": 500},
            "underwear": {"min": 22, "max": 48}
        }

        # Product name templates by category
        self.product_templates = {
            "shoes": [
                "{brand} {material} {silhouette} - {gender} - {color}",
                "{material} {silhouette} - {gender}'s - {color} ({sole_type} Sole)",
                "{color} {material} {silhouette} - {gender}'s Edition",
                "Eco {material} {silhouette}s - {color} ({gender}'s)",
                "{material} {silhouette} {gender}'s - {color} {edition}"
            ],
            "socks": [
                "{material} {sock_type} Socks - {color}",
                "{gender}'s {material} {sock_type} - {color}",
                "Eco {material} Socks - {color} ({sock_type})",
                "{color} {material} {sock_type} Socks"
            ],
            "apparel": [
                "{material} {apparel_type} - {gender}'s - {color}",
                "{color} {material} {apparel_type} - {gender}'s",
                "Eco {material} {apparel_type} - {color}",
                "{gender}'s {material} {apparel_type} in {color}"
            ]
        }

        # Additional product attributes
        self.sock_types = ["ankle", "crew", "no-show", "knee-high", "compression", "athletic"]
        self.apparel_types = ["t-shirt", "hoodie", "cardigan", "vest", "jacket", "pants", "shorts", "dress"]
        self.sole_types = ["rubber", "cork", "foam", "recycled", "natural", "comfort"]
        self.brands = ["Manybirds", "TinyBirds", "SkyBirds", "EcoBirds", "UrbanBirds"]

    def generate_id(self) -> int:
        """Generate a random ID in the style of Shopify"""
        return random.randint(5000000000000, 9999999999999)

    def generate_datetime(self, days_ago_min: int = 30, days_ago_max: int = 730) -> str:
        """Generate a random datetime string with more realistic distribution"""
        # Weight recent dates more heavily
        if random.random() < 0.4:  # 40% chance of recent date
            days_ago = random.randint(1, 90)
        else:
            days_ago = random.randint(days_ago_min, days_ago_max)
        
        dt = datetime.now() - timedelta(days=days_ago)
        # Add some time variation
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        dt = dt.replace(hour=hours, minute=minutes, second=seconds)
        return dt.strftime("%Y-%m-%dT%H:%M:%S-07:00")

    def get_product_category_details(self, product_type: str) -> Dict[str, Any]:
        """Get category-specific details"""
        category_map = {
            "Shoes": "shoes",
            "Socks": "socks", 
            "Apparel": "apparel",
            "Accessories": "accessories",
            "Bags": "bags",
            "Insoles": "insoles",
            "Laces": "laces",
            "Care Products": "care products",
            "Gift Cards": "gift cards",
            "Underwear": "underwear"
        }
        return category_map.get(product_type, "accessories")

    def generate_product_name(self, product_type: str) -> Dict[str, str]:
        """Generate product title and handle based on type"""
        category = self.get_product_category_details(product_type)
        gender = random.choice(self.genders)
        material = random.choice(self.materials)
        color = random.choice(self.colors)
        edition = random.choice(self.editions)
        brand = random.choice(self.brands)
        
        if category == "shoes":
            silhouette = random.choice(self.silhouettes)
            sole_type = random.choice(self.sole_types)
            template = random.choice(self.product_templates["shoes"])
            title = template.format(
                brand=brand, material=material.title(), silhouette=silhouette, 
                gender=gender.title(), color=color.title(), sole_type=sole_type.title(),
                edition=edition.title()
            )
        elif category == "socks":
            sock_type = random.choice(self.sock_types)
            template = random.choice(self.product_templates["socks"])
            title = template.format(
                material=material.title(), sock_type=sock_type.title(),
                color=color.title(), gender=gender.title()
            )
            silhouette = sock_type
        elif category == "apparel":
            apparel_type = random.choice(self.apparel_types)
            template = random.choice(self.product_templates["apparel"])
            title = template.format(
                material=material.title(), apparel_type=apparel_type.title(),
                color=color.title(), gender=gender.title()
            )
            silhouette = apparel_type
        else:
            # Generic template for other categories
            title = f"{brand} {material.title()} {product_type.rstrip('s')} - {color.title()}"
            silhouette = product_type.lower()
        
        # Clean up title
        title = title.replace("'s's", "'s").replace("  ", " ")
        handle = title.lower().replace("'s", "").replace(" ", "-").replace("(", "").replace(")", "").replace("--", "-")
        
        return {
            "title": title, 
            "handle": handle, 
            "gender": gender, 
            "material": material, 
            "color": color, 
            "silhouette": silhouette,
            "brand": brand,
            "category": category
        }

    def generate_enhanced_tags(self, product_info: Dict[str, str], price: float, product_type: str) -> List[str]:
        """Generate enhanced Manybirds-style tags"""
        carbon_score = round(random.uniform(1.8, 5.2), 2)
        price_tier = random.choice(self.price_tiers)
        edition = random.choice(self.editions)
        
        tags = [
            f"Manybirds::carbon-score = {carbon_score}",
            f"Manybirds::cfId = color-{product_info['handle']}-{product_info['color']}-new",
            f"Manybirds::complete = {random.choice(['true', 'false'])}",
            f"Manybirds::edition = {edition}",
            f"Manybirds::gender = {product_info['gender']}",
            f"Manybirds::hue = {product_info['color']}",
            f"Manybirds::master = {product_info['handle']}",
            f"Manybirds::material = {product_info['material']}",
            f"Manybirds::price-tier = {price_tier}",
            f"Manybirds::silhouette = {product_info['silhouette']}",
            f"Manybirds::category = {product_info['category']}",
            "loop::returnable = true"
        ]
        
        # Add category-specific tags
        if product_info['category'] == 'shoes':
            tags.extend([
                "shoprunner",
                f"YCRF_{product_info['gender']}-{product_info['silhouette']}-shoes",
                f"YGroup_ygroup_{product_info['handle']}"
            ])
        
        # Add conditional tags
        additional_tags = [
            "sustainable" if random.choice([True, False]) else None,
            "machine-washable" if product_info['category'] in ['socks', 'apparel'] else None,
            "limited-edition" if edition == "limited" else None,
            "new-arrival" if random.random() < 0.3 else None,
            "bestseller" if random.random() < 0.2 else None,
            "eco-friendly" if product_info['material'] in ['recycled', 'organic cotton', 'bamboo'] else None,
            f"made-with-{product_info['material']}" if product_info['material'] != 'cotton' else None,
            "comfort-fit" if random.choice([True, False]) else None
        ]
        
        tags.extend([tag for tag in additional_tags if tag])
        return tags

    def generate_size_options(self, product_info: Dict[str, str], product_type: str) -> List[str]:
        """Generate appropriate size options based on product type and gender"""
        category = product_info['category']
        gender = product_info['gender']
        
        # Map category to size type
        if category in ['shoes', 'insoles']:
            if gender in ['men', 'women', 'kids', 'toddler', 'baby']:
                size_category = gender
            else:  # unisex
                size_category = random.choice(['men', 'women'])
        elif category in ['socks', 'apparel', 'underwear']:
            size_category = category
        else:
            size_category = 'accessories'
        
        available_sizes = self.sizes.get(size_category, self.sizes['accessories'])
        
        # Select number of sizes based on category
        if category == 'shoes':
            num_sizes = random.randint(6, min(12, len(available_sizes)))
        elif category in ['apparel', 'socks']:
            num_sizes = random.randint(4, min(8, len(available_sizes)))
        else:
            num_sizes = random.randint(1, min(4, len(available_sizes)))
        
        return random.sample(available_sizes, num_sizes)

    def generate_variants(self, product_id: int, product_info: Dict[str, str], base_price: float, product_type: str) -> List[Dict[str, Any]]:
        """Generate product variants with enhanced realism"""
        variants = []
        sizes = self.generate_size_options(product_info, product_type)
        
        for i, size in enumerate(sizes):
            variant_id = self.generate_id()
            
            # Generate realistic SKU
            brand_code = product_info['brand'][:2].upper()
            category_code = product_info['category'][:2].upper()
            color_code = product_info['color'][:2].upper()
            size_code = size.replace('.', '').replace('-', '')[:3].upper()
            random_suffix = ''.join(random.choices('0123456789', k=3))
            sku = f"{brand_code}{category_code}{color_code}{size_code}{random_suffix}"
            
            # More realistic price variation
            if product_info['category'] == 'shoes':
                # Larger sizes might cost slightly more
                size_factor = 1 + (i * 0.02)
            else:
                size_factor = 1
                
            price_variation = random.uniform(0.98, 1.03) * size_factor
            variant_price = round(base_price * price_variation, 2)
            
            # Compare at price (MSRP)
            if random.choice([True, False]):  # 50% chance of having compare price
                compare_price = round(variant_price * random.uniform(1.15, 1.67), 2)
            else:
                compare_price = None
            
            # Weight calculation based on category and size
            base_weights = {
                'shoes': random.randint(280, 520),
                'socks': random.randint(50, 120),
                'apparel': random.randint(150, 400),
                'accessories': random.randint(30, 200),
                'bags': random.randint(200, 800)
            }
            
            base_weight = base_weights.get(product_info['category'], 100)
            weight_factor = 1 + (i * 0.08)
            weight = int(base_weight * weight_factor)
            
            # Availability - make some sizes out of stock
            availability_rate = 0.75 if product_info.get('edition') != 'limited' else 0.6
            available = random.random() < availability_rate
            
            variant = {
                "id": variant_id,
                "title": size,
                "option1": size,
                "option2": None,
                "option3": None,
                "sku": sku,
                "requires_shipping": True,
                "taxable": True,
                "featured_image": None,
                "available": available,
                "price": f"{variant_price:.2f}",
                "grams": weight,
                "compare_at_price": f"{compare_price:.2f}" if compare_price else None,
                "position": i + 1,
                "product_id": product_id,
                "created_at": self.generate_datetime(60, 800),
                "updated_at": self.generate_datetime(1, 60)
            }
            variants.append(variant)
        
        return variants

    def generate_images(self, product_id: int, product_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate realistic product images"""
        images = []
        
        # Different image counts by category
        if product_info['category'] == 'shoes':
            num_images = random.randint(4, 8)
            image_types = ["angle", "side", "top", "detail", "lifestyle", "back", "sole", "worn"]
        elif product_info['category'] in ['apparel', 'bags']:
            num_images = random.randint(3, 6)
            image_types = ["front", "back", "detail", "lifestyle", "flat", "worn"]
        else:
            num_images = random.randint(2, 4)
            image_types = ["main", "detail", "lifestyle", "angle"]
        
        for i in range(num_images):
            image_id = self.generate_id()
            image_type = random.choice(image_types)
            
            # Generate realistic filename
            color_code = product_info['color'].replace(' ', '_').lower()
            category_code = product_info['category'].replace(' ', '_').lower()
            filename = f"{product_info['brand']}_{category_code}_{color_code}_{image_type}_{random.randint(1000, 9999)}.jpg"
            
            # CDN URL with realistic structure
            cdn_path = f"products/{product_info['handle']}/{filename}"
            src = f"https://cdn.shopify.com/s/files/1/1104/4168/{cdn_path}?v={random.randint(1650000000, 1700000000)}"
            
            # Image dimensions based on type
            if image_type in ["lifestyle", "worn"]:
                dimensions = random.choice([(1920, 1280), (1600, 1200), (2000, 1500)])
            else:
                dimensions = random.choice([(1600, 1600), (2000, 2000), (1200, 1200)])
            
            image = {
                "id": image_id,
                "created_at": self.generate_datetime(60, 800),
                "position": i + 1,
                "updated_at": self.generate_datetime(1, 60),
                "product_id": product_id,
                "variant_ids": [],
                "src": src,
                "width": dimensions[0],
                "height": dimensions[1]
            }
            images.append(image)
        
        return images

    def generate_product_description(self, product_info: Dict[str, str], product_type: str) -> str:
        """Generate category-specific product descriptions"""
        category = product_info['category']
        material = product_info['material']
        color = product_info['color']
        
        descriptions = {
            'shoes': [
                f"Step into sustainable comfort with our {material} {product_info['silhouette']}s. Crafted with premium {material} and designed for everyday wear, these {color} shoes combine style with environmental responsibility.",
                f"Experience the perfect blend of comfort and sustainability with these {color} {material} {product_info['silhouette']}s. Machine washable and designed to last, they're perfect for the modern conscious consumer.",
                f"Our {color} {material} {product_info['silhouette']}s represent the future of footwear - comfortable, sustainable, and effortlessly stylish. Made with responsibly sourced materials.",
                f"Discover uncompromising comfort with our premium {material} {product_info['silhouette']}s in {color}. Ethically made, incredibly comfortable, and designed for life's everyday adventures."
            ],
            'socks': [
                f"Cozy up in our {material} {product_info['silhouette']} socks. Made with premium {material} fiber, these {color} socks are soft, breathable, and perfect for all-day comfort.",
                f"Step up your sock game with our {color} {material} socks. Featuring moisture-wicking properties and a comfortable fit, they're ideal for any activity.",
                f"Experience next-level comfort with our {material} socks in {color}. Naturally antimicrobial and temperature regulating for happy feet all day long."
            ],
            'apparel': [
                f"Embrace sustainable style with our {material} {product_info['silhouette']} in {color}. Soft, comfortable, and responsibly made for the conscious wardrobe.",
                f"Our {color} {material} {product_info['silhouette']} combines timeless style with modern sustainability. Perfect for layering or wearing solo.",
                f"Crafted from premium {material}, this {color} {product_info['silhouette']} offers unmatched comfort and style for the environmentally conscious."
            ]
        }
        
        category_descriptions = descriptions.get(category, [
            f"Discover our premium {material} {product_type.lower()} in {color}. Thoughtfully designed with sustainability and comfort in mind.",
            f"Our {color} {material} {product_type.lower()} represents quality craftsmanship and environmental responsibility.",
            f"Experience the perfect blend of style and sustainability with our {material} {product_type.lower()} in {color}."
        ])
        
        return random.choice(category_descriptions)

    def generate_product(self) -> Dict[str, Any]:
        """Generate a complete product with enhanced realism"""
        product_id = self.generate_id()
        product_type = random.choice(self.product_types)
        product_info = self.generate_product_name(product_type)
        
        # Determine pricing
        category = self.get_product_category_details(product_type)
        price_range = self.base_prices.get(category, self.base_prices["accessories"])
        
        # Add some premium pricing for certain materials/editions
        price_multiplier = 1.0
        if product_info['material'] in ['cashmere', 'alpaca', 'merino']:
            price_multiplier *= random.uniform(1.2, 1.5)
        if 'limited' in product_info.get('edition', ''):
            price_multiplier *= random.uniform(1.1, 1.3)
            
        base_price = random.randint(price_range["min"], price_range["max"])
        base_price = int(base_price * price_multiplier)
        
        # Timestamps with realistic distribution
        created_at = self.generate_datetime(180, 1200)
        updated_at = self.generate_datetime(1, 180)
        published_at = self.generate_datetime(30, 365)
        
        # Generate variants first to get size options
        variants = self.generate_variants(product_id, product_info, base_price, product_type)
        
        product = {
            "id": product_id,
            "title": product_info["title"],
            "handle": product_info["handle"],
            "body_html": self.generate_product_description(product_info, product_type),
            "published_at": published_at,
            "created_at": created_at,
            "updated_at": updated_at,
            "vendor": product_info["brand"],
            "product_type": product_type,
            "tags": self.generate_enhanced_tags(product_info, base_price, product_type),
            "variants": variants,
            "images": self.generate_images(product_id, product_info),
            "options": [
                {
                    "id": self.generate_id(),
                    "product_id": product_id,
                    "name": "Size",
                    "position": 1,
                    "values": [variant["option1"] for variant in variants]
                }
            ]
        }
        
        return product

    def generate_dataset(self, num_products: int = 25) -> Dict[str, List[Dict[str, Any]]]:
        """Generate a complete enhanced dataset"""
        products = []
        
        print(f"Generating {num_products} enhanced Manybirds-style products...")
        
        for i in range(num_products):
            product = self.generate_product()
            products.append(product)
            print(f"Generated product {i+1}/{num_products}: {product['title']}")
        
        return {"products": products}

def main():
    generator = EnhancedManybirdsDataGenerator()
    
    # Generate 25 diverse products
    dataset = generator.generate_dataset(25)
    
    # Save to file
    output_file = "enhanced_manybirds_test_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Generated {len(dataset['products'])} products and saved to {output_file}")
    
    # Display detailed summary
    print("\n📊 Enhanced Dataset Summary:")
    print(f"Total Products: {len(dataset['products'])}")
    
    # Category breakdown
    categories = {}
    brands = {}
    materials = {}
    total_variants = 0
    total_images = 0
    
    for product in dataset['products']:
        # Count categories
        category = product['product_type']
        categories[category] = categories.get(category, 0) + 1
        
        # Count brands
        brand = product['vendor']
        brands[brand] = brands.get(brand, 0) + 1
        
        # Count materials (from tags)
        for tag in product['tags']:
            if 'material =' in tag:
                material = tag.split('= ')[1]
                materials[material] = materials.get(material, 0) + 1
                break
        
        total_variants += len(product['variants'])
        total_images += len(product['images'])
    
    print(f"Total Variants: {total_variants}")
    print(f"Total Images: {total_images}")
    print(f"Average Variants per Product: {total_variants/len(dataset['products']):.1f}")
    print(f"Average Images per Product: {total_images/len(dataset['products']):.1f}")
    
    print("\n📋 Product Categories:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    
    print("\n🏷️ Brands:")
    for brand, count in sorted(brands.items()):
        print(f"  {brand}: {count}")
    
    print("\n🧵 Materials:")
    for material, count in sorted(materials.items()):
        print(f"  {material}: {count}")

if __name__ == "__main__":
    main()
