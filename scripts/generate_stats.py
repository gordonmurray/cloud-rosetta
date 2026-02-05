#!/usr/bin/env python3
"""
Generate database statistics for releases
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def generate_stats(db_path: str = "db/cloud_rosetta.db") -> str:
    """Generate markdown stats for the database"""
    
    if not Path(db_path).exists():
        return "# Database Statistics\n\nDatabase not found."
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = []
    stats.append("# Cloud Rosetta Database Statistics")
    stats.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Get database version
    try:
        cursor.execute("SELECT version, updated_at FROM db_version ORDER BY id DESC LIMIT 1")
        version_info = cursor.fetchone()
        if version_info:
            stats.append(f"**Database Version:** {version_info[0]}")
            stats.append(f"**Last Updated:** {version_info[1]}")
    except:
        stats.append("**Database Version:** Unknown")
    
    # Resource mappings count
    cursor.execute("SELECT COUNT(*) FROM resource_mappings")
    resource_count = cursor.fetchone()[0]
    stats.append(f"\n## Resource Mappings: {resource_count}")
    
    # Break down by category
    cursor.execute("""
        SELECT resource_category, COUNT(*) 
        FROM resource_mappings 
        GROUP BY resource_category 
        ORDER BY COUNT(*) DESC
    """)
    
    stats.append("\n### By Category:")
    for category, count in cursor.fetchall():
        stats.append(f"- **{category.title()}**: {count} resources")
    
    # Instance types count
    cursor.execute("SELECT COUNT(*) FROM instance_types")
    instance_count = cursor.fetchone()[0]
    stats.append(f"\n## Instance Types: {instance_count}")
    
    # Break down by provider
    cursor.execute("""
        SELECT provider, COUNT(*) 
        FROM instance_types 
        GROUP BY provider 
        ORDER BY provider
    """)
    
    stats.append("\n### By Provider:")
    for provider, count in cursor.fetchall():
        stats.append(f"- **{provider.upper()}**: {count} instance types")
    
    # Regions count
    cursor.execute("SELECT COUNT(*) FROM regions")
    region_count = cursor.fetchone()[0]
    stats.append(f"\n## Regions: {region_count}")
    
    cursor.execute("""
        SELECT provider, COUNT(*) 
        FROM regions 
        GROUP BY provider 
        ORDER BY provider
    """)
    
    stats.append("\n### By Provider:")
    for provider, count in cursor.fetchall():
        stats.append(f"- **{provider.upper()}**: {count} regions")
    
    # Images count
    cursor.execute("SELECT COUNT(*) FROM images")
    image_count = cursor.fetchone()[0]
    stats.append(f"\n## OS Images: {image_count}")
    
    # Instance family distribution
    cursor.execute("""
        SELECT family, provider, COUNT(*) 
        FROM instance_types 
        WHERE family IS NOT NULL 
        GROUP BY family, provider 
        ORDER BY family, provider
    """)
    
    stats.append(f"\n## Instance Families")
    current_family = None
    for family, provider, count in cursor.fetchall():
        if family != current_family:
            stats.append(f"\n### {family.title()}")
            current_family = family
        stats.append(f"- **{provider.upper()}**: {count} instances")
    
    # Recent changes (if available)
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM pricing_history 
            WHERE date(effective_date) = date('now')
        """)
        recent_updates = cursor.fetchone()[0]
        if recent_updates > 0:
            stats.append(f"\n## Recent Updates")
            stats.append(f"- **Today**: {recent_updates} pricing updates")
    except:
        pass
    
    # Sample mappings
    stats.append(f"\n## Sample Resource Mappings")
    
    cursor.execute("""
        SELECT aws_type, ovh_type, hetzner_type, resource_category 
        FROM resource_mappings 
        WHERE aws_type IS NOT NULL 
        LIMIT 10
    """)
    
    stats.append("\n| AWS | OVH | Hetzner | Category |")
    stats.append("|-----|-----|---------|----------|")
    
    for aws, ovh, hetzner, category in cursor.fetchall():
        ovh_display = ovh if ovh else "—"
        hetzner_display = hetzner if hetzner else "—"
        stats.append(f"| `{aws}` | `{ovh_display}` | `{hetzner_display}` | {category} |")
    
    # Sample instance mappings
    stats.append(f"\n## Sample Instance Type Mappings")
    
    # Get equivalent instances across providers
    cursor.execute("""
        SELECT 
            a.instance_type as aws_type,
            o.instance_type as ovh_type,
            h.instance_type as hetzner_type,
            a.vcpu, a.memory_gb
        FROM instance_types a
        LEFT JOIN instance_types o ON ABS(a.vcpu - o.vcpu) <= 1 
                                    AND ABS(a.memory_gb - o.memory_gb) <= 2 
                                    AND o.provider = 'ovh'
        LEFT JOIN instance_types h ON ABS(a.vcpu - h.vcpu) <= 1 
                                    AND ABS(a.memory_gb - h.memory_gb) <= 2 
                                    AND h.provider = 'hetzner'
        WHERE a.provider = 'aws' 
          AND (o.instance_type IS NOT NULL OR h.instance_type IS NOT NULL)
        LIMIT 5
    """)
    
    stats.append("\n| AWS | OVH | Hetzner | vCPU | RAM |")
    stats.append("|-----|-----|---------|------|-----|")
    
    for aws, ovh, hetzner, vcpu, memory in cursor.fetchall():
        ovh_display = ovh if ovh else "—"
        hetzner_display = hetzner if hetzner else "—"
        stats.append(f"| `{aws}` | `{ovh_display}` | `{hetzner_display}` | {vcpu} | {memory}GB |")
    
    # Footer
    stats.append(f"\n---")
    stats.append(f"\n*Database generated by Cloud Rosetta • Visit [github.com/gordonmurray/cloud-rosetta](https://github.com/gordonmurray/cloud-rosetta)*")
    
    conn.close()
    return "\n".join(stats)


def main():
    """Generate stats for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate database statistics")
    parser.add_argument("--db", default="db/cloud_rosetta.db", 
                       help="Path to database file")
    parser.add_argument("--output", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    stats = generate_stats(args.db)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(stats)
        print(f"Stats written to {args.output}")
    else:
        print(stats)


if __name__ == "__main__":
    main()