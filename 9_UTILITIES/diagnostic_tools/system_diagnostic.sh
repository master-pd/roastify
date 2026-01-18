#!/bin/bash

# Roastify Pro - Complete System Diagnostic Tool
# Diagnoses and fixes common issues

# ... [Previous code remains, adding diagnostic features]

run_comprehensive_diagnostic() {
    echo -e "${CYAN}🔍 Running comprehensive diagnostic...${NC}"
    
    # System check
    check_system_health
    
    # Docker check
    check_docker_health
    
    # Database check
    check_database_health
    
    # Redis check
    check_redis_health
    
    # Network check
    check_network_health
    
    # Bot check
    check_bot_health
    
    # API check
    check_api_health
    
    # Generate report
    generate_diagnostic_report
    
    # Auto-fix issues
    auto_fix_issues
    
    echo -e "${GREEN}✓ Diagnostic completed${NC}"
}

generate_diagnostic_report() {
    REPORT_FILE="/tmp/roastify_diagnostic_$(date +%Y%m%d_%H%M%S).html"
    
    cat > $REPORT_FILE << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Roastify Pro Diagnostic Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .pass { color: green; }
        .fail { color: red; }
        .warning { color: orange; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Roastify Pro Diagnostic Report</h1>
    <p>Generated: $(date)</p>
    
    <h2>System Health</h2>
    <table>
        <tr><th>Component</th><th>Status</th><th>Details</th></tr>
        $(generate_system_rows)
    </table>
    
    <h2>Recommendations</h2>
    <ul>
        $(generate_recommendations)
    </ul>
</body>
</html>
EOF
    
    echo -e "${GREEN}📄 Report generated: $REPORT_FILE${NC}"
}