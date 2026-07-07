# Quant Benchmark — gemma 12B  Q4_K_M vs Q3_K_M


## Q4_K_M (current) — `gemma4:12b`

- **Disk:** 8.0 GB · **VRAM resident:** 8.0 GB · cold-load 24.1s
- **Avg latency:** 16.6s · **Avg throughput:** 5.9 tok/s · **answered:** 5/5
- **Large-context (num_ctx 8192) probe:** SURVIVED (57.1s)

  Sample answers:
  - **[EN]** What is Bid Security (EMD) and what percentage of the estimated value is it?
    → Bid Security (also called Earnest Money Deposit, EMD) is taken to safeguard against a bidder withdrawing or altering the bid during its validity, or failing to furnish Performance Security. It is normally 2% to 5% of the estimated value of 
  - **[EN]** Who can be exempted from paying EMD?
    → Micro and Small Enterprises (MSEs) and units registered with relevant authorities may be exempted from EMD as per government rules.
  - **[HI]** धरोहर राशि (EMD) क्या होती है और यह अनुमानित मूल्य का कितना प्रतिशत होती है?
    → धरोहर राशि (Bid Security या Earnest Money Deposit - EMD) एक सुरक्षा के रूप में ली जाती है ताकि कोई बोलीदाता अपनी बोली को रद्द न करे, उसमें बदलाव न करे या प्रदर्शन सुरक्षा (Performance Security) प्रदान करने में विफल न हो। यह आमतौर पर खरीद के
  - **[HI]** असफल बोलीदाताओं को EMD कब वापस की जाती है?
    → असफल बोलीदाताओं का EMD अनुबंध दिए जाने के बाद (after the contract is awarded) वापस किया जाता है।
  - **[HIN]** EMD exempt kin logon ko milta hai?
    → Micro and Small Enterprises (MSEs) aur relevant authorities ke saath registered units ko government rules ke anusar EMD se chhoot (exempted) mil sakti hai.

## Q3_K_M (new) — `gemma3-q3km:12b`

- **Disk:** 6.63 GB · **VRAM resident:** 6.63 GB · cold-load 14.3s
- **Avg latency:** 13.2s · **Avg throughput:** 5.0 tok/s · **answered:** 5/5
- **Large-context (num_ctx 8192) probe:** SURVIVED (45.8s)

  Sample answers:
  - **[EN]** What is Bid Security (EMD) and what percentage of the estimated value is it?
    → Bid Security (also called Earnest Money Deposit, EMD) safeguards against bid withdrawal/alteration or failure to furnish Performance Security. It's normally 2% to 5% of the estimated value.
  - **[EN]** Who can be exempted from paying EMD?
    → Micro and Small Enterprises (MSEs) and units registered with relevant authorities may be exempted from EMD as per government rules.
  - **[HI]** धरोहर राशि (EMD) क्या होती है और यह अनुमानित मूल्य का कितना प्रतिशत होती है?
    → Bid Security (EMD) को बोली वापस लेने या बदलने से बचाने के लिए लिया जाता है। यह आमतौर पर खरीद के अनुमानित मूल्य का 2% से 5% होता है, जैसा कि बोली दस्तावेज में निर्दिष्ट है।
  - **[HI]** असफल बोलीदाताओं को EMD कब वापस की जाती है?
    → अनुबंध प्रदान किए जाने के बाद।
  - **[HIN]** EMD exempt kin logon ko milta hai?
    → Micro aur Small Enterprises (MSEs) aur relevant authorities mein registered units ko EMD se exemption milta hai.
