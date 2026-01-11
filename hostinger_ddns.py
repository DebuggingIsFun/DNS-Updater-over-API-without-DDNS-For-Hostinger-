# Hostinger DDNS own version

import hostinger_api
from hostinger_api.rest import ApiException
from hostinger_api import Configuration
import os
import requests
from dotenv import load_dotenv, set_key
import time

#### Variables from .env file
load_dotenv() ## need to load .env file
API_TOKEN = os.getenv("API_TOKEN","")
LAST_KNOWN_IP = os.getenv("LAST_KNOWN_IP","0.0.0.0")
DOMAINS = [d.strip() for d in os.getenv("DOMAINS", "domain.tld").split(",")]
SUBDOMAINS = [s.strip() for s in os.getenv("SUBDOMAINS", "somesubdomain").split(",")]
TTL=int(os.getenv("TTL","60"))

#### Check if .env is correct
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print("CONFIG LOADED:")
print(f"DOMAINS ({len(DOMAINS)}): {DOMAINS}")
print(f"SUBDOMAINS ({len(SUBDOMAINS)}): {SUBDOMAINS}")
print(f"TTL: {TTL}")
print(f"LAST_KNOWN_IP: {LAST_KNOWN_IP}")
print("-" * 50)

#### Check Current IP vs Last known
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)

        response.raise_for_status()

        ip_data = response.json()

        return ip_data['ip']
    except requests.RequestException as e:
        print (f"Network Error: {e} ")
        return None
    except (KeyError, ValueError) as e:
        print(f"Bad response format: {e}")
        return None

def check_if_update_needed():
    public_ip = get_public_ip()
    
    print(f"Current public IP: {public_ip}")
    print(f"Logged public IP:  {LAST_KNOWN_IP}")

    if public_ip is not None and public_ip != LAST_KNOWN_IP:
        print(f"IP changed: {LAST_KNOWN_IP} -> {public_ip}")
        return True, public_ip
    elif public_ip == LAST_KNOWN_IP:
        print("IP's match, nothing to do")
        return False, LAST_KNOWN_IP
    else:
        print("ERROR: Could not get public IP")
        return False, None


#### Update Records Method
def update_dns_record(domain, subdomain, ip, ttl, api_token):
    """
    Updates A record for a subdomain via Hostinger API.
    
    Args:
        domain (str): e.g., "example.com"
        subdomain (str): e.g., "ente" (full FQDN: ente.example.com)
        ip (str): IPv4 address to set
        ttl (int): TTL in seconds (default: 60)
        api_token (str): Hostinger API token (uses env if None)
    
    Returns:
        bool: True if successful
    """
    # Use env token if not provided
    token = api_token or os.getenv("API_TOKEN")
    if not token:
        print("ERROR: No API_TOKEN provided")
        return False
    
    configuration = Configuration(access_token=token)
    
    try:
        with hostinger_api.ApiClient(configuration) as api_client:
            api_instance = hostinger_api.DNSZoneApi(api_client)
            
            # Build the nested structure (minimal steps)
            record = hostinger_api.DNSV1ZoneUpdateRequestZoneInnerRecordsInner(
                content=ip
            )
            
            zone_entry = hostinger_api.DNSV1ZoneUpdateRequestZoneInner(
                name=subdomain,
                type="A",
                ttl=ttl,
                records=[record]
            )
            
            update_request = hostinger_api.DNSV1ZoneUpdateRequest(
                overwrite=True,
                zone=[zone_entry]
            )
            
            # API call
            response = api_instance.update_dns_records_v1(
                domain=domain,
                dnsv1_zone_update_request=update_request
            )
            
            print(f"SUCCESS: Updated {subdomain}.{domain} → {ip}")
            return True
            
    except hostinger_api.rest.ApiException as e:
        print(f"API ERROR {e.status}: {e.body}")
        if e.statusin[401,403]:
            print("-> Check API Token")
        elif e.status == 400:
            print("-> Check domain and subdomain spelling")
        return False

    except Exception as e:
        print(f"ERROR updating {subdomain}.{domain}: {e}")
        return False

#### Updating env file for the new IP Methode
def update_last_ip_in_env(new_ip, env_file=".env"):
    """
    Updates LAST_KNOWN_IP in .env file.
    """
    try:
        # Load current .env (optional, for safety)
        load_dotenv(env_file)
        
        # Update the specific key in .env file
        set_key(env_file, "LAST_KNOWN_IP", new_ip)
        
        print(f"UPDATED .env: LAST_KNOWN_IP = {new_ip}")
        return True
        
    except Exception as e:
        print(f"ERROR updating .env: {e}")
        return False

def main():
    ip_changed, public_ip = check_if_update_needed()
    
    if ip_changed == True:
        print("\nStart the update")
        print("=" * 50)
        
        success_count = 0
        total_records = len(DOMAINS) * len(SUBDOMAINS)
        
        # OUTER LOOP: Each domain
        for domain in DOMAINS:
            print(f"\nDomain: {domain}")
            print("-" * 30)
            domain_success = 0
            
            # INNER LOOP: Subdomains for this domain
            for subdomain in SUBDOMAINS:
                full_record = f"{subdomain}.{domain}"
                print(f"  Updating {full_record}...")
                
                if update_dns_record(domain, subdomain, public_ip, TTL, API_TOKEN):
                    print(f"Success")
                    domain_success += 1
                    success_count += 1
                    time.sleep(1.0)
                else:
                    print(f"Failed")
            
            print(f"Result: {domain_success}/{len(SUBDOMAINS)}")
        
        # FINAL SUMMARY
        print("\n" + "=" * 60)
        success_rate = (success_count / total_records * 100) if total_records > 0 else 0
        print(f"Total: {success_count}/{total_records} ({success_rate:.1f}%)")
        print("=" * 60)
        
        update_last_ip_in_env(public_ip)
        
        # MANUAL PAUSE
        #print("\nPress ENTER to exit...")
        #input()
    else:
        print("No IP change - skipping")

if __name__ == '__main__':
    main()