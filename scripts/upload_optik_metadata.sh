#!/bin/bash

# ============================================
# UPLOAD OPTIK METADATA TO PINATA
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Pinata credentials
PINATA_JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI1NGYwMWM3ZC0zMmU3LTQzYTAtYmI3ZS1mNzI0MGY3OTE4ZTIiLCJlbWFpbCI6ImpheXNwZWVyMTVAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6ImQ2OTY3YzgwNWMxZTEyMjg0MmFiIiwic2NvcGVkS2V5U2VjcmV0IjoiZWZkZTcyYjllNDg3NzVjYjUzZmIyNTFhMjdlMzI1OGQ0ZmE4NDUzNDc1YzVkNmY1NzIwM2MzOGI5MGU4ZWU4ZSIsImV4cCI6MTgwNDkzOTk5OX0.M9o7hBzXwNyeUj4xNptph71KTVO1sLEIO9dDMTjSUxw"
PINATA_API_KEY="d6967c805c1e122842ab"
PINATA_SECRET_KEY="efde72b9e48775cb53fb251a27e3258d4fa8453475c5d6f57203c38b90e8ee8e"

# Metadata files to upload
METADATA_DIR="/home/kali/Dapp_Optik/optik-platform/apps/audit"
METADATA_FILES=(
    "optik-metadata.json"
    "optik-token.json"
)

# Registry files
REGISTRY_FILE="/home/kali/Dapp_Optik/optik-platform/apps/agents/registry.json"
MANAGED_CONTEXT_FILE="/home/kali/Dapp_Optik/optik-platform/apps/managed_context/metadata.json"
MCP_SERVERS_FILE="/home/kali/Dapp_Optik/optik-platform/apps/mcp_servers.json"

echo -e "${BLUE}🚀 OPTIK METADATA UPLOAD TO PINATA${NC}"
echo -e "${YELLOW}========================================${NC}"

# Test Pinata connection
echo -e "${BLUE}🔍 Testing Pinata connection...${NC}"
response=$(curl -s -X GET "https://api.pinata.cloud/data/testAuthentication" \
  -H "Authorization: Bearer $PINATA_JWT")

if echo "$response" | grep -q "Congratulations"; then
    echo -e "${GREEN}✅ Pinata connection successful!${NC}"
else
    echo -e "${RED}❌ Pinata connection failed!${NC}"
    echo "$response"
    exit 1
fi

# Create upload results file
RESULTS_FILE="/home/kali/Dapp_Optik/pinata_upload_results.json"
echo '{"uploads": []}' > "$RESULTS_FILE"

# Function to upload file to Pinata
upload_to_pinata() {
    local file_path="$1"
    local file_name=$(basename "$file_path")
    
    echo -e "${BLUE}📤 Uploading: $file_name${NC}"
    
    response=$(curl -s -X POST "https://api.pinata.cloud/pinning/pinFileToIPFS" \
        -H "Authorization: Bearer $PINATA_JWT" \
        -F "file=@$file_path" \
        -F "pinataMetadata={\"name\":\"$file_name\",\"keyvalues\":{\"app\":\"optik-platform\",\"type\":\"metadata\"}}")
    
    if echo "$response" | grep -q "IpfsHash"; then
        ipfs_hash=$(echo "$response" | jq -r '.IpfsHash')
        gateway_url="https://plum-gigantic-mammal-466.mypinata.cloud/ipfs/$ipfs_hash"
        
        echo -e "${GREEN}✅ Success!${NC}"
        echo -e "   IPFS Hash: $ipfs_hash"
        echo -e "   Gateway URL: $gateway_url"
        
        # Update results
        jq --arg file "$file_name" --arg hash "$ipfs_hash" --arg url "$gateway_url" \
            '.uploads += [{"file": $file, "ipfs_hash": $hash, "gateway_url": $url}]' \
            "$RESULTS_FILE" > "$RESULTS_FILE.tmp" && mv "$RESULTS_FILE.tmp" "$RESULTS_FILE"
        
        return 0
    else
        echo -e "${RED}❌ Failed to upload $file_name${NC}"
        echo "$response"
        return 1
    fi
}

# Upload metadata files
echo -e "\n${YELLOW}📋 Uploading Audit Metadata Files...${NC}"
for file in "${METADATA_FILES[@]}"; do
    if [ -f "$METADATA_DIR/$file" ]; then
        upload_to_pinata "$METADATA_DIR/$file"
    else
        echo -e "${RED}❌ File not found: $METADATA_DIR/$file${NC}"
    fi
done

# Upload registry files
echo -e "\n${YELLOW}📋 Uploading Registry Files...${NC}"
if [ -f "$REGISTRY_FILE" ]; then
    upload_to_pinata "$REGISTRY_FILE"
else
    echo -e "${RED}❌ File not found: $REGISTRY_FILE${NC}"
fi

if [ -f "$MANAGED_CONTEXT_FILE" ]; then
    upload_to_pinata "$MANAGED_CONTEXT_FILE"
else
    echo -e "${RED}❌ File not found: $MANAGED_CONTEXT_FILE${NC}"
fi

if [ -f "$MCP_SERVERS_FILE" ]; then
    upload_to_pinata "$MCP_SERVERS_FILE"
else
    echo -e "${RED}❌ File not found: $MCP_SERVERS_FILE${NC}"
fi

# Create comprehensive metadata collection
echo -e "\n${YELLOW}📦 Creating comprehensive metadata collection...${NC}"

COLLECTION_FILE="/tmp/optik_metadata_collection.json"
cat > "$COLLECTION_FILE" << EOF
{
  "name": "Optik Platform Metadata Collection",
  "description": "Complete metadata collection for Optik automated dApp factory",
  "version": "1.0.0",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)",
  "platform": "optikcoin.com",
  "gateway": "https://plum-gigantic-mammal-466.mypinata.cloud",
  "includes": [
    "NFT metadata templates",
    "Agent registry",
    "MCP server configurations",
    "Platform audit data",
    "Managed context metadata"
  ],
  "properties": {
    "type": "metadata-collection",
    "platform": "optik",
    "version": "1.0.0"
  },
  "links": {
    "website": "https://optikcoin.com",
    "documentation": "https://docs.optikcoin.com",
    "github": "https://github.com/optikcoin/platform"
  }
}
EOF

upload_to_pinata "$COLLECTION_FILE"

# Summary
echo -e "\n${GREEN}🎉 UPLOAD COMPLETE!${NC}"
echo -e "${YELLOW}================================${NC}"

if [ -f "$RESULTS_FILE" ]; then
    echo -e "${BLUE}📊 Upload Summary:${NC}"
    jq -r '.uploads[] | "• \(.file): \(.ipfs_hash)"' "$RESULTS_FILE"
    
    echo -e "\n${BLUE}🔗 Gateway URLs:${NC}"
    jq -r '.uploads[] | "• \(.file): \(.gateway_url)"' "$RESULTS_FILE"
    
    # Save to .env.local for easy access
    echo -e "\n${YELLOW}💾 Saving to .env.local...${NC}"
    first_hash=$(jq -r '.uploads[0].ipfs_hash' "$RESULTS_FILE")
    
    if [ "$first_hash" != "null" ]; then
        # Update .env.local with IPFS hashes
        sed -i "/OPTIK_METADATA_IPFS_HASH/d" /home/kali/Dapp_Optik/optik-platform/apps/.env.local
        echo "OPTIK_METADATA_IPFS_HASH=$first_hash" >> /home/kali/Dapp_Optik/optik-platform/apps/.env.local
        
        sed -i "/OPTIK_METADATA_COLLECTION_URL/d" /home/kali/Dapp_Optik/optik-platform/apps/.env.local
        echo "OPTIK_METADATA_COLLECTION_URL=https://plum-gigantic-mammal-466.mypinata.cloud/ipfs/$first_hash" >> /home/kali/Dapp_Optik/optik-platform/apps/.env.local
        
        echo -e "${GREEN}✅ Added to .env.local${NC}"
    fi
fi

echo -e "\n${GREEN}🚀 Your Optik metadata is now on IPFS!${NC}"
echo -e "${BLUE}🌐 Access via your custom gateway: https://plum-gigantic-mammal-466.mypinata.cloud${NC}"
echo -e "${YELLOW}📄 Results saved to: $RESULTS_FILE${NC}"
