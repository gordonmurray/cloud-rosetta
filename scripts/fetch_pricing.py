#!/usr/bin/env python3
"""
Cloud Pricing Fetcher
Fetches pricing data from various cloud providers
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PricingFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'cloud-rosetta-pricing-fetcher/1.0'
        })
    
    def fetch_aws_pricing(self) -> Dict[str, Any]:
        """Fetch AWS pricing data"""
        logger.info("Fetching AWS pricing data...")
        
        try:
            # AWS EC2 pricing (simplified - real implementation would use AWS API)
            # For now, we'll use Infracost's pricing data format
            aws_pricing = {
                "instances": {
                    "t3.nano": {"price": 0.0052, "vcpu": 2, "memory": 0.5},
                    "t3.micro": {"price": 0.0104, "vcpu": 2, "memory": 1},
                    "t3.small": {"price": 0.0208, "vcpu": 2, "memory": 2},
                    "t3.medium": {"price": 0.0416, "vcpu": 2, "memory": 4},
                    "t3.large": {"price": 0.0832, "vcpu": 2, "memory": 8},
                    "m5.large": {"price": 0.096, "vcpu": 2, "memory": 8},
                    "m5.xlarge": {"price": 0.192, "vcpu": 4, "memory": 16},
                    "m5.2xlarge": {"price": 0.384, "vcpu": 8, "memory": 32},
                    "c5.large": {"price": 0.085, "vcpu": 2, "memory": 4},
                    "c5.xlarge": {"price": 0.17, "vcpu": 4, "memory": 8},
                    "r5.large": {"price": 0.126, "vcpu": 2, "memory": 16},
                    "r5.xlarge": {"price": 0.252, "vcpu": 4, "memory": 32},
                },
                "storage": {
                    "gp2": {"price_per_gb": 0.10},
                    "gp3": {"price_per_gb": 0.08},
                    "io1": {"price_per_gb": 0.125, "iops_price": 0.065},
                },
                "updated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Fetched {len(aws_pricing['instances'])} AWS instance types")
            return aws_pricing
            
        except Exception as e:
            logger.error(f"Failed to fetch AWS pricing: {e}")
            return {"instances": {}, "storage": {}}
    
    def fetch_ovh_pricing(self) -> Dict[str, Any]:
        """Fetch OVH pricing data"""
        logger.info("Fetching OVH pricing data...")
        
        try:
            # OVH doesn't have a public pricing API, so we'll use scraped data
            # In a real implementation, you might scrape their pricing pages
            # or use their private APIs if you have access
            
            ovh_pricing = {
                "instances": {
                    # d2 series (discovery/flex)
                    "d2-2": {"price": 0.0084, "vcpu": 1, "memory": 2},
                    "d2-4": {"price": 0.0168, "vcpu": 2, "memory": 4},
                    "d2-8": {"price": 0.0337, "vcpu": 4, "memory": 8},
                    
                    # b2 series (balanced)
                    "b2-7": {"price": 0.0278, "vcpu": 2, "memory": 7},
                    "b2-15": {"price": 0.0556, "vcpu": 4, "memory": 15},
                    "b2-30": {"price": 0.1111, "vcpu": 8, "memory": 30},
                    "b2-60": {"price": 0.2222, "vcpu": 16, "memory": 60},
                    
                    # c2 series (compute)
                    "c2-7": {"price": 0.0417, "vcpu": 2, "memory": 7},
                    "c2-15": {"price": 0.0833, "vcpu": 4, "memory": 15},
                    "c2-30": {"price": 0.1667, "vcpu": 8, "memory": 30},
                    
                    # r2 series (memory)
                    "r2-15": {"price": 0.0556, "vcpu": 2, "memory": 15},
                    "r2-30": {"price": 0.1111, "vcpu": 4, "memory": 30},
                    "r2-60": {"price": 0.2222, "vcpu": 8, "memory": 60},
                },
                "storage": {
                    "classic": {"price_per_gb": 0.04},
                    "high-speed": {"price_per_gb": 0.16},
                },
                "updated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Fetched {len(ovh_pricing['instances'])} OVH instance types")
            return ovh_pricing
            
        except Exception as e:
            logger.error(f"Failed to fetch OVH pricing: {e}")
            return {"instances": {}, "storage": {}}
    
    def fetch_hetzner_pricing(self) -> Dict[str, Any]:
        """Fetch Hetzner pricing data using their API"""
        logger.info("Fetching Hetzner pricing data...")
        
        try:
            # Hetzner has a public API for pricing
            response = self.session.get('https://api.hetzner.cloud/v1/pricing')
            response.raise_for_status()
            
            data = response.json()
            pricing = data.get('pricing', {})
            
            hetzner_pricing = {
                "instances": {},
                "storage": {},
                "updated_at": datetime.now().isoformat()
            }
            
            # Parse server types pricing
            if 'server_types' in pricing:
                for server_type, price_data in pricing['server_types'].items():
                    hourly_price = float(price_data['price_hourly']['gross'])
                    hetzner_pricing['instances'][server_type] = {
                        "price": hourly_price,
                        "monthly_price": hourly_price * 730  # Approximate hours per month
                    }
            
            # Parse volume pricing
            if 'volume' in pricing:
                volume_price = float(pricing['volume']['price_per_gb_month']['gross'])
                hetzner_pricing['storage']['volume'] = {
                    "price_per_gb_month": volume_price
                }
            
            logger.info(f"Fetched {len(hetzner_pricing['instances'])} Hetzner server types")
            return hetzner_pricing
            
        except Exception as e:
            logger.error(f"Failed to fetch Hetzner pricing: {e}")
            # Fallback to hardcoded prices
            return {
                "instances": {
                    "cx11": {"price": 0.0052, "vcpu": 1, "memory": 2},
                    "cx21": {"price": 0.0089, "vcpu": 2, "memory": 4},
                    "cx31": {"price": 0.0137, "vcpu": 2, "memory": 8},
                    "cx41": {"price": 0.0274, "vcpu": 4, "memory": 16},
                    "cx51": {"price": 0.0548, "vcpu": 8, "memory": 32},
                    
                    "cpx11": {"price": 0.0068, "vcpu": 2, "memory": 2},
                    "cpx21": {"price": 0.0116, "vcpu": 3, "memory": 4},
                    "cpx31": {"price": 0.0219, "vcpu": 4, "memory": 8},
                    "cpx41": {"price": 0.0438, "vcpu": 8, "memory": 16},
                },
                "storage": {
                    "volume": {"price_per_gb_month": 0.0476}
                },
                "updated_at": datetime.now().isoformat()
            }
    
    def fetch_all_pricing(self) -> Dict[str, Any]:
        """Fetch pricing from all providers"""
        logger.info("Fetching pricing from all cloud providers...")
        
        all_pricing = {
            "aws": self.fetch_aws_pricing(),
            "ovh": self.fetch_ovh_pricing(), 
            "hetzner": self.fetch_hetzner_pricing(),
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        
        return all_pricing
    
    def save_pricing_data(self, pricing_data: Dict[str, Any], filename: str = "pricing_data.json"):
        """Save pricing data to file"""
        with open(filename, 'w') as f:
            json.dump(pricing_data, f, indent=2)
        logger.info(f"Pricing data saved to {filename}")


def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch cloud provider pricing data")
    parser.add_argument("--provider", choices=["aws", "ovh", "hetzner", "all"], 
                       default="all", help="Which provider to fetch")
    parser.add_argument("--output", default="pricing_data.json", 
                       help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    fetcher = PricingFetcher()
    
    if args.provider == "all":
        pricing_data = fetcher.fetch_all_pricing()
    elif args.provider == "aws":
        pricing_data = {"aws": fetcher.fetch_aws_pricing()}
    elif args.provider == "ovh":
        pricing_data = {"ovh": fetcher.fetch_ovh_pricing()}
    elif args.provider == "hetzner":
        pricing_data = {"hetzner": fetcher.fetch_hetzner_pricing()}
    
    fetcher.save_pricing_data(pricing_data, args.output)
    
    # Print summary
    for provider, data in pricing_data.items():
        if provider != "metadata" and "instances" in data:
            instance_count = len(data["instances"])
            print(f"{provider.upper()}: {instance_count} instance types")


if __name__ == "__main__":
    main()