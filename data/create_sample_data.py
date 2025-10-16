"""
Script to create sample Excel data for testing
"""

import pandas as pd
from pathlib import Path

# Sample business data
data = {
    'Business Name': [
        'Coffee Paradise',
        'Tech Solutions Inc',
        'Green Garden Restaurant',
        'Digital Marketing Pro',
        'Fitness Center Plus',
        'Book Haven',
        'Auto Repair Shop',
        'Fashion Boutique',
        'Pet Grooming Service',
        'Home Cleaning Experts',
        # Some test cases with issues
        '',  # Missing name
        'Invalid Phone Business',
        'Bad Website URL',
    ],
    'Description': [
        'Local coffee shop with artisan drinks',
        'IT consulting and software development',
        'Organic farm-to-table dining',
        'SEO and social media marketing',
        'Modern gym with personal training',
        'Independent bookstore',
        'Full service auto repair',
        'Trendy clothing and accessories',
        'Professional pet care',
        'Residential and commercial cleaning',
        'Test business',
        'Testing invalid phone',
        'Testing bad website',
    ],
    'Website': [
        '',  # No website
        'https://techsolutions.com',  # Has website
        '',  # No website
        'https://digitalmarketingpro.com',  # Has website
        'https://fitnessplus.com',  # Has website
        '',  # No website
        '',  # No website
        'https://fashionboutique.shop',  # Has website
        '',  # No website
        'https://cleanexperts.com',  # Has website
        '',
        'https://example.com',
        'not a valid url',  # Invalid URL
    ],
    'Phone': [
        '+12025551001',
        '+12025551002',
        '+12025551003',
        '+12025551004',
        '+12025551005',
        '+12025551006',
        '+12025551007',
        '+12025551008',
        '+12025551009',
        '+12025551010',
        '+12025551011',
        'invalid',  # Invalid phone
        '+12025551012',
    ],
    'Google Maps Link': [
        'https://maps.google.com/?q=CoffeeParadise',
        'https://maps.google.com/?q=TechSolutions',
        'https://maps.google.com/?q=GreenGarden',
        'https://maps.google.com/?q=DigitalMarketing',
        'https://maps.google.com/?q=FitnessPlus',
        'https://maps.google.com/?q=BookHaven',
        'https://maps.google.com/?q=AutoRepair',
        'https://maps.google.com/?q=FashionBoutique',
        'https://maps.google.com/?q=PetGrooming',
        'https://maps.google.com/?q=CleanExperts',
        '',
        '',
        'https://maps.google.com/?q=TestBusiness',
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_path = Path(__file__).parent / 'data.xlsx'
df.to_excel(output_path, index=False, engine='openpyxl')

print(f"✅ Sample Excel file created: {output_path}")
print(f"   Total rows: {len(df)}")
print(f"   Businesses with websites: {(df['Website'] != '').sum()}")
print(f"   Businesses without websites: {(df['Website'] == '').sum()}")
