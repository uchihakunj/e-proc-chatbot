# Role-based e-Procurement functional test report

## Meaning of the status

A **Pass** means the live service returned a non-empty answer, at least one source, and no known provider/transport error. It is a functional-grounding screen; policy/legal correctness should be reviewed against the full response and cited documents.

## Summary

- **total questions:** 50
- **pass:** 50
- **review:** 0
- **source coverage percent:** 100.0
- **followup coverage percent:** 48.0
- **median latency seconds:** 9.063
- **p95 latency seconds:** 15.647

### By role

| Role | Questions | Pass | Review |
| --- | ---: | ---: | ---: |
| Department Buyer | 15 | 15 | 0 |
| Department Operator | 10 | 10 | 0 |
| General User | 10 | 10 | 0 |
| Vendor / Bidder | 15 | 15 | 0 |

## BUYER-01 — Department Buyer — Pass

**Question:** Hamare department ko 40 desktops kharidne hain. Sabse pehle kya karein?

**Response time:** 7.096 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, GFRupdatedupto31012026.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Aapke department ko 40 desktops kharidne ke liye sabse pehle ye steps follow karne honge:

*   **Purchase Committee banana:** Chunki aapka office Rs. 50,000 ya usse zyada ka purchase kar raha hai, toh ek purchase committee banana zaroori hai. Ismein departmental accounts officer/accounts in-charge aur technical knowledge wale officers shaamil hone chahiye.
*   **Tender conditions taiyaar karna:** Tender conditions clear aur unambiguous honi chahiye. Bidder GST-registered hona chahiye aur taxes separately quote karne honge.
*   **Sample ka intezam:** Agar pre-purchase sample nahi mil sakta, toh supplier ko item demonstrate karna hoga. Agar wo bhi possible nahi hai, toh manufacturing site par inspection ka right reserve karna hoga.
*   **Contract execute karna:** Purchase order issue karne se pehle contract execute karna hoga. Agar L1 (lowest bid) ko accept nahi kiya jaata, toh reasons in writing record karne honge.

40 desktops ke liye ye process follow karna hoga. Agar aap chahte hain ki main aapko is process ke baare mein aur detail mein bataun, toh main aapki help kar sakta hoon.

📘 स्रोत: Store Purchase Rule CG

## BUYER-02 — Department Buyer — Pass

**Question:** Office ke liye printers lene hain. Tender karna padega ya GeM chalega?

**Response time:** 5.266 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Printers lene ke liye pehle check karna hoga ki GeM par printers available hain ya nahi. Agar GeM par printers hain aur unke rates aur specifications aapke office ki zarurat se match karte hain, toh GeM se hi kharid sakte hain. GeM se kharidne se pehle buyer ko technical specifications, seller credibility, L1 price, economy aur quality check karni hogi. Agar GeM par printers nahi hain ya aapke paas Finance Department ki written concurrence hai, tabhi aap tender kar sakte hain. Agar GeM par printers nahi hain aur CSIDC e-Standard par bhi nahi hain, toh Rule 4 tender procedure ke through procurement karna padega.

📘 स्रोत: Store Purchase Rule CG

## BUYER-03 — Department Buyer — Pass

**Question:** Agar GeM par laptop available hai to kya wahi se lena compulsory hai?

**Response time:** 11.699 seconds  
**Sources:** store purchase rule cg.pdf, GFRupdatedupto31012026.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Agar GeM par laptop available hai to wahi se lena compulsory nahi hai, lekin pehle buyer ko check karna padega ki technical specifications, seller credibility, L1 price, economy, aur quality sahi hai ya nahi. Agar department ko lagta hai ki GeM se lena theek nahi hai, to ve tender kar sakte hain, lekin iske liye Finance Department se concerned administrative department ke through written concurrence lena zaroori hai.

📘 स्रोत: Store Purchase Rule CG

## BUYER-04 — Department Buyer — Pass

**Question:** Hamare office ko projector kharidna hai. Kaunsi procurement method sahi rahegi?

**Response time:** 13.369 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

💡 Answer
Original question “Hamare office ko projector kharidna hai. Kaunsi procurement method sahi rahegi?” ko exact intent procurement_method_selection ke saath preserve kiya gaya hai. Is specific workflow ke liye reliable section available nahi hua, isliye kisi related lekin alag process ke steps nahi diye gaye hain. Relevant official section check karein.

## BUYER-05 — Department Buyer — Pass

**Question:** Purchase start karne se pehle kis-kis se approval lena hota hai?

**Response time:** 7.446 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Purchase start karne se pehle approval ke liye ye steps follow karne padte hain:

**Proprietary Article Certificate (PAC) ke liye:**
- Appendix 4 ke prescribed form mein PAC obtain karna hota hai
- Newspapers aur government/department website par claim/objection notice publish karna hota hai, jisme kam se kam 30 days ka time diya jaata hai
- Objections resolve hone ke baad, proposed supplier ke rates aur justification lena hota hai
- Purchase committee recommendation deti hai - acceptance, rejection ya negotiation ke liye
- Uske baad competent approval lena hota hai

**General Purchase Committee Approval:**
- Agar office Rs. 50,000 ya usse zyada per year ka purchase kar raha hai to purchase committee banani padti hai
- Committee mein departmental accounts officer/accounts in-charge aur technical knowledge wale officers hona zaroori hain

**Contract Execution ke liye:**
- Purchase order issue karne se pehle contract execute karna hota hai
- Agar L1/lowest tender accept nahi kiya jaata to written reasons record karne padte hain

**Repeat Supply Orders ke liye:**
- Original order se six months ke andar repeat supply order issue nahi kiya ja sakta
- Original order quantity ka sirf 25% tak hi ho sakta hai

📘 स्रोत: Store Purchase Rule CG, Public Procurement Manual

## BUYER-06 — Department Buyer — Pass

**Question:** Technical specification banate waqt kya dhyan rakhna chahiye?

**Response time:** 4.903 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf, Compilation of CVC Circulars and Guidelines.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Technical specification banate waqt ye baatein dhyan mein rakhni chahiye:

*   **Level playing field aur widest competition ensure karna:** Specification aisi honi chahiye jo sabhi vendors ke liye barabar ho aur zyada se zyada log participate kar saken.
*   **Unambiguous aur precise hona:** Koi bhi confusion na ho, sab kuch clear aur exact likha hona chahiye.
*   **Objective aur functional hona:** Specification sirf zaroori cheezon par focus kare, koi faltu features na hon jo cost badhaaye.
*   **Broad-based aur generic hona:** Aisi specification jo common materials aur equipment ko allow kare, taaki koi restriction na ho.
*   **National standards follow karna:** Preference BIS mark wale goods ko deni chahiye. Agar BIS standards nahi hain, to international standards use kiye ja sakte hain, lekin iske liye written reasons record karne honge.
*   **Detailed specifications use karna:** Jahan possible ho, detailed specifications ke basis par procurement karein, na ki sirf sample ke basis par. Sample sirf successful bidder ke liye bulk production se pehle approve karwana chahiye.

📘 स्रोत: Public Procurement Manual 2024

## BUYER-07 — Department Buyer — Pass

**Question:** Kya hum specification mein HP ya Dell ka naam likh sakte hain?

**Response time:** 3.217 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf, Compilation of CVC Circulars and Guidelines.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Nahi, aap specification mein HP ya Dell jaise brand names nahi likh sakte. CVC guidelines ke according, open tender system mein brand names specify karna guidelines ke against hai. Yeh doosre brands, including domestic manufacturers ko tender mein participate karne ka opportunity nahi deta.

Guidelines kehti hain ki personal computers ke liye generalized specifications use karni chahiye aur brand names mention nahi karne chahiye. Yeh tab tak apply hota hai jab tak DG dwara rate contract conclude nahi ho jaata.

📘 स्रोत: CVC Circulars & Guidelines

## BUYER-08 — Department Buyer — Pass

**Question:** Budget approve ho gaya hai. Ab next step kya hai?

**Response time:** 4.157 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf, Précis  e-Procurement Project.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Budget approve ho gaya hai, lekin context mein next step ke baare mein koi jaankari nahi di gayi hai. Document sirf e-Procurement Project ke costs ke baare mein bataata hai, jo Rs. 36.90 Crore aur Rs. 42.3 Crore hain. Iske alaava, Manual for Procurement of Goods 2024 mein re-delegation of powers aur contingent expenditure ke rules hain, lekin project budget approve hone ke baad kya karna hai, yeh nahi bataya gaya hai.

📘 स्रोत: Public Procurement Manual 2024, Integrated e-Procurement Project 2.0 & 3.0 Documents

## BUYER-09 — Department Buyer — Pass

**Question:** Agar sirf ek vendor qualify kare to kya purchase ho sakti hai?

**Response time:** 10.022 seconds  
**Sources:** GFR2017_HINDI.pdf, Store_Purhase_Rules_28.01.2021.pdf, FInal_GFR_upto_31_07_2024.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Haan, agar sirf ek vendor qualify karta hai to purchase ho sakti hai. Yeh GFR ke Rule 166 ke according allowed hai.

Iske liye do conditions hain:
1. Jab sirf ek hi firm ke paas expected goods ka manufacturing ka right ho.
2. Emergency mein jab expected goods ko kisi particular source se hi kharidna zaroori ho.

Is case mein, decision ka reason record karna hoga aur competent authority se approval lena hoga.

📘 स्रोत: GFR2017_HINDI.pdf

## BUYER-10 — Department Buyer — Pass

**Question:** Lowest price dene wale ko hi order dena padta hai kya?

**Response time:** 14.948 seconds  
**Sources:** GFR2017_HINDI.pdf, FInal_GFR_upto_31_07_2024.pdf, store purchase rule cg.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

नहीं, lowest price dene wale ko hi order dena zaroori nahi hai. Context mein yeh information nahi di gayi hai ki lowest bid (L1) ko hi contract dena hoga.

GFR aur store purchase rules mein sirf tender process, timelines, aur purchase limits ke baare mein bataya gaya hai, lekin yeh clear nahi kiya gaya ki lowest price hi final decision ka basis hoga.

📘 स्रोत: General Financial Rules 2017 (Hindi) और Store Purchase Rules CG

## BUYER-11 — Department Buyer — Pass

**Question:** Purchase Order issue hone ke baad department ko kya karna hota hai?

**Response time:** 6.638 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Purchase Order issue hone ke baad department ko kya karna hota hai, yeh information available documents mein nahi hai. Context mein sirf Standing Committee ke functions, non-compliance ke action, aur supply base assessment ke baare mein information hai, lekin Purchase Order issue hone ke baad ka process ya department ke responsibilities ke baare mein kuch nahi diya gaya hai.

📘 स्रोत: Public Procurement Manual (English)

## BUYER-12 — Department Buyer — Pass

**Question:** Vendor ne galat material deliver kar diya. Ab kya process rahega?

**Response time:** 9.773 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Vendor ne galat material deliver kar diya hai, toh contract ke terms ke according action lena padega. Manual for Procurement of Goods, 2024 ke according, delivery date expire hone ke baad bhi agar outstanding quantity hai, toh contract cancel kiya ja sakta hai.

Process kuch is tarah se hoga:

1.  **Notice bhejna:** Department Admin ko supplier ko ek formal notice bhejna hoga, jismein bataya jaye ki galat material deliver hua hai aur contract ka breach hua hai.
2.  **Details maangna:** Supplier se poora record maanga jayega ki kitna material supply hua, kitna inspect hua, aur kitna dispatch ya tender ke liye ready hai.
3.  **Extension dena (agar zaroori ho):** Agar supplier ko thoda time chahiye, toh delivery period extend kiya ja sakta hai, lekin yeh unke risk aur cost par hoga.
4.  **Contract Cancellation:** Agar supplier extended time mein bhi sahi material deliver nahi karta, toh contract cancel kar diya jayega.

Yeh process Manual for Procurement of Goods, Second Edition, 2024 ke Annexure 23 mein diya gaya hai.

📘 स्रोत: Manual for Procurement of Goods 2024

## BUYER-13 — Department Buyer — Pass

**Question:** Agar delivery late ho jaye to department kya action le sakta hai?

**Response time:** 5.293 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, AuctionManual_FA.pdf  
**Follow-ups:** How does reverse auction work? | How is EMD handled in auctions? | When is the auction EMD refunded?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Available documents mein delivery late hone ke liye department ke specific action ke baare mein koi jaankari nahi di gayi hai.

📘 स्रोत: store purchase rule cg.pdf

## BUYER-14 — Department Buyer — Pass

**Question:** Payment release karne se pehle kya verify karna hota hai?

**Response time:** 10.806 seconds  
**Sources:** GFR2017_HINDI.pdf, FInal_GFR_upto_31_07_2024.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Payment release karne se pehle kya verify karna hota hai, yeh context mein clear nahi hai. Available documents mein loan disbursement, claims processing, aur procurement rules ke baare mein information hai, lekin payment release ke liye specific verification steps ka detail nahi diya gaya hai.

📘 स्रोत: GFR2017_HINDI.pdf, FInal_GFR_upto_31_07_2024.pdf

## BUYER-15 — Department Buyer — Pass

**Question:** Office ke liye AC ka AMC karwana hai. Process kya rahega?

**Response time:** 6.819 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

💡 Answer
Original question “Office ke liye AC ka AMC karwana hai. Process kya rahega?” ko exact intent procurement_planning ke saath preserve kiya gaya hai. Is specific workflow ke liye reliable section available nahi hua, isliye kisi related lekin alag process ke steps nahi diye gaye hain. Relevant official section check karein.

## GENERAL-01 — General User — Pass

**Question:** Hamare office ko naye laptops chahiye. Humein process kahan se start karna chahiye?

**Response time:** 0.021 seconds  
**Sources:** Chhattisgarh Store Purchase Rules, Manual for Procurement of Goods 2024  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

💡 Answer
First, the department should consolidate and record the requirement for the laptops, including quantity, purpose, users, delivery timeline, estimated value, and budget head. After that, it should prepare generic and competition-friendly technical specifications, confirm budget availability, obtain the required administrative and financial approvals, and then check whether suitable laptops are available on GeM or another approved procurement channel. Only after these steps should the department choose the permitted procurement method and create the GeM Bid or Tender.

📋 Process
1. Record the full requirement, including users, purpose, and delivery timeline.
2. Prepare generic, measurable technical specifications.
3. Estimate the total cost and confirm budget availability.
4. Obtain the applicable administrative approval and financial sanction.
5. Create the purchase indent or procurement request.
6. Check GeM and other approved channels for availability.
7. Apply the Store Purchase Rules and delegated powers to choose the lawful procurement method.
8. Then proceed with the GeM Bid or Tender process.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024.

## GENERAL-02 — General User — Pass

**Question:** Government office mein saman kharidne ka normal process kya hota hai?

**Response time:** 4.768 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf, GFRupdatedupto31012026.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Government office mein saman kharidne ka normal process e-procurement portal ke through hota hai. Pehle, department ek tender notice (NIT) release karta hai jismein requirements aur eligibility criteria di hoti hai. Interested vendors (suppliers) portal par registration karke apna technical bid (PQ bid) aur price bid (financial bid) submit karte hain. Technical bid ki evaluation hoti hai, aur agar vendor qualify ho jaata hai, toh price bid open ki jaati hai. Sabse kam price wala vendor (L1) select hota hai aur use purchase order issue kiya jaata hai. Agar tender ki value kam hai, toh GFR ke according direct purchase ya store purchase rules follow kiye ja sakte hain.

📘 स्रोत: Manual for Procurement of Goods 2024, General Financial Rules (GFR)

## GENERAL-03 — General User — Pass

**Question:** GeM aur e-Procurement portal mein difference kya hai?

**Response time:** 4.747 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf, store purchase rule cg.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Answer
GeM goods/services procurement ka government marketplace aur channel hai, jab applicable rules permit karein. State e-Procurement portal Tender publish/manage karne, Bid receipt/opening aur Corrigendum ke liye use hota hai. Pehle current Chhattisgarh rules aur approvals ke under lawful route choose karein, phir appropriate channel use karein. Governing rule confirm kiye bina generic monetary thresholds apply na karein.

📘 Source: Manual for Procurement of Goods 2024; Chhattisgarh Store Purchase Rules

## GENERAL-04 — General User — Pass

**Question:** Mujhe samajh nahi aa raha ki GeM use karun ya tender nikalu.

**Response time:** 15.559 seconds  
**Sources:** store purchase rule cg.pdf, GFRupdatedupto31012026.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

GeM use karna chahiye jab aapke goods ya services aur unke rates aur specifications GeM par available hain. GeM se kharidne ke liye, aapko uska prescribed process follow karna hoga. Order karne se pehle, aapko technical specifications, seller credibility, L1 price, economy, aur quality check karni chahiye. Agar aap tender nikalna chahte hain, toh aapko Finance Department se written concurrence lena hoga, jo concerned administrative department ke through milega.

Agar aapke items GeM par available nahi hain, toh aap CSIDC e-Standard se kharid sakte hain agar unke rates aur specifications wahan available hain. Agar item GeM ya CSIDC dono par available nahi hai, toh aapko Rule 4 tender procedure se procure karna hoga.

📘 स्रोत: Store Purchase Rule CG

## GENERAL-05 — General User — Pass

**Question:** Kya har government purchase tender se hi hoti hai?

**Response time:** 23.233 seconds  
**Sources:** store purchase rule cg.pdf, FInal_GFR_upto_31_07_2024.pdf, Store_Purhase_Rules_28.01.2021.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Government procurement normally tender system se hoti hai, lekin har purchase ke liye tender zaroori nahi hai.

Context ke according:
- Rule 4 aur 4.1 kehta hai ki government procurement normally tender system se hoti hai, lekin iska matlab ye nahi ki har purchase tender se hi hogi.
- Store Purchase Rules 2021 mein open tender method ki details di gayi hain, jo specific value ranges ke liye apply hoti hai.
- GFR mein Purchase Committee ke through purchase ka provision hai, jahan GeM portal par item available nahi ho to Rs. 50,000 se Rs. 5,00,000 tak ke items purchase kiye ja sakte hain.

Isliye, har government purchase tender se nahi hoti. Kuch purchases Purchase Committee ke through ya direct procurement se bhi ho sakti hain.

📘 स्रोत: Store Purchase Rules 2021, General Financial Rules (GFR)

## GENERAL-06 — General User — Pass

**Question:** Agar office ke liye furniture lena ho to kya procedure hota hai?

**Response time:** 12.438 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, GFRupdatedupto31012026.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Office ke liye furniture lene ke liye neeche diye gaye procedure follow karne honge:

Agar furniture ki total value Rs. 50,000 ya usse zyada hai, to office mein ek purchase committee banani hogi jisme departmental accounts officer/accounts in-charge aur technical knowledge wale officers shaamil honge.

Tender conditions clear aur unambiguous hone chahiye. Furniture ke liye jo bhi supplier tender de, usse GST-registered hona zaroori hai aur taxes alag se quote karne honge. Agar pre-purchase sample nahi milta hai, to supplier ko item demonstrate karne ka chance dena chahiye, aur agar woh bhi possible nahi hai, to buyer ke paas manufacturing site par inspect karne ka right hona chahiye.

EMD (Earnest Money Deposit) normally estimated purchase value ka 1% hota hai. Successful bidder ka EMD retain kar liya jaata hai, aur baaki bidders ka EMD finalisation ke 15 days ke andar refund karna hota hai. Agar office ek registered small/cottage unit ya valid recognised startup hai, to EMD exemption mil sakti hai, lekin iske liye required certificate/proof submit karna padega.

Purchase order issue karne se pehle, kam se kam actual purchase value ka 3% security deposit lena zaroori hai. EMD ya security deposit cash mein accept nahi kiye ja sakte.

Agar L1 (lowest tender) accept nahi kiya jaata hai, to written mein reasons record karne honge. Contract purchase order issue karne se pehle execute karna hoga.

Repeat supply order ke liye, original order ke 6 months baad tak order issue nahi kiya ja sakta aur yeh original order quantity ke 25% se zyada nahi ho sakta.

📘 स्रोत: store purchase rule cg

## GENERAL-07 — General User — Pass

**Question:** Single Tender ka matlab simple language mein batao.

**Response time:** 10.138 seconds  
**Sources:** FInal_GFR_upto_31_07_2024.pdf, Chatbot_Capabilities.pdf, GFR2017_HINDI.pdf, Store_Purhase_Rules_28.01.2021.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Single Tender ka matlab hai jab koi bhi cheez sirf ek hi company se kharidi jaati hai. Yeh tab hota hai jab user department ko pata ho ki sirf ek hi firm uss cheez ka manufacturer hai. Iske alawa, agar kisi procurement ke terms aur conditions revise karne hain, toh procuring entity fundamental rules ko modify nahi kar sakti.

📘 स्रोत: Final_GFR_upto_31_07_2024.pdf

## GENERAL-08 — General User — Pass

**Question:** Limited Tender kab use karte hain?

**Response time:** 8.934 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Limited Tender ka use tab kiya jaata hai jab estimated annual purchases Rs. 50,001 se Rs. 3,00,000 ke beech hoti hain. Is method mein kam se kam three manufacturers, authorised representatives, ya registered manufacturers ko invite karna hota hai. Agar estimated value of goods Rs. Fifty Lakhs tak hai, tab bhi Limited Tender Enquiry method use kiya ja sakta hai.

📘 स्रोत: Store Purchase Rule CG, Public Procurement Manual, General Financial Rules

## GENERAL-09 — General User — Pass

**Question:** Department ko office stationery kharidni ho to kya karna padega?

**Response time:** 9.877 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, GFRupdatedupto31012026.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

💡 Answer
Original question “Department ko office stationery kharidni ho to kya karna padega?” ko exact intent procurement_planning ke saath preserve kiya gaya hai. Is specific workflow ke liye reliable section available nahi hua, isliye kisi related lekin alag process ke steps nahi diye gaye hain. Relevant official section check karein.

## GENERAL-10 — General User — Pass

**Question:** Chhattisgarh mein government procurement kaise hoti hai?

**Response time:** 3.385 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

💡 Answer
Chhattisgarh procurement mein channels/platforms aur procurement methods alag cheezein hain. GeM aur State e-Procurement portal selected route ko execute karne ke channels hain; registration ya login procurement method nahi hai.

📋 Major procurement routes
1. GeM procurement — item aur applicable rules permit karein to relevant GeM method use hota hai.
2. Tender procurement — Open, Limited ya Single Tender sirf applicable conditions mein.
3. Permitted direct purchase — current rules, value conditions, delegated powers aur approvals allow karein tabhi.
4. Inter-departmental/undertaking purchase — rules permit karein to doosre government department ya undertaking se purchase.
5. Emergency/special procurement — exceptional route; recorded reasons aur competent approval chahiye, unrestricted direct purchase nahi.
6. Foreign/global purchase — sirf jab applicable GFR/rules aur approvals is route ko support karein.

Pehle route choose karein, phir appropriate GeM ya e-Procurement channel use karein. Registration, vendor login aur DSC setup bidder/portal activities hain, procurement methods nahi.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024

## OPERATOR-01 — Department Operator — Pass

**Question:** Naya tender create karna hai. Process batao.

**Response time:** 3.391 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Naya tender create karne ke liye, aapko pehle decide karna hoga ki kis type ka tender chahiye. Agar aapko market explore karna hai aur specifications finalize karne hain, toh two-stage tendering system use kar sakte hain. Isme pehle Expression of Interest (EoI) bids invite kiye jaate hain.

EoI bids in situations mein invite kiye ja sakte hain:
- Agar aap detailed specifications khud se formulate nahi kar pa rahe hain aur bidders se technical inputs chahiye.
- Agar subject matter mein rapid technological advances ya market fluctuations hain.
- Agar aap research, experiment, study ya development ke liye contract karna chahte hain.
- Agar bidder se detailed survey ya investigation ki expectation hai.

Less complex cases mein, pre-NIT conference ke through market consultation bhi kaafi hai.

Iske liye aapko Manual for Procurement of Goods 2024 refer karna chahiye.

📘 स्रोत: Manual for Procurement of Goods 2024

## OPERATOR-02 — Department Operator — Pass

**Question:** Tender publish kaise karte hain portal par?

**Response time:** 4.153 seconds  
**Sources:** Manual_Offline_Tenders_v.1.0.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Portal par tender publish karne ke liye aapko 'ADVANCE SEARCH' option use karna padta hai. Yeh feature aapko Tender, Latest News, Latest Notice, aur Heldesk Contact details dekhne mein madad karta hai. Iske alawa, tender document mein Section I hota hai jismein 'Notice Inviting Tender (NIT)' aur uska Appendix 'Tender Information Summary (TIS)' hota hai, jo portal par publish karne ke liye zaroori hota hai.

📘 स्रोत: Manual_Offline_Tenders_v.1.0.pdf

## OPERATOR-03 — Department Operator — Pass

**Question:** Tender ki last date badhani ho to kya karna padega?

**Response time:** 13.603 seconds  
**Sources:** Chatbot_Capabilities.pdf, Store_Purhase_Rules_28.01.2021.pdf, store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Tender ki last date badhani ho to tender notice mein mentioned process follow karna padega. Agar tender offline hai to registered post se extension request bhejni hogi, lekin yeh sirf tab possible hai agar tender notice mein pehle se mention ho. Online tender ke liye, tender portal par ja kar extension ke liye official process follow karni padegi.

Agar last date ke baad tender receive hua hai to woh open nahi kiya jaata aur wapas bhej diya jaata hai. Tender ki validity aur last date badhane ke liye tender issuing authority se permission lena zaroori hai.

📘 स्रोत: Store Purchase Rules 28.01.2021

## OPERATOR-04 — Department Operator — Pass

**Question:** Corrigendum issue karne ka process kya hai?

**Response time:** 12.449 seconds  
**Sources:** CHiPS_Corrigendum_Issuance_Manual.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Answer
Is action ke liye relevant CHiPS portal manual aur authorised role use karein. DSC/browser issue mein documented compatibility, Java/extension aur certificate checks hi karein. Bid opening required authentication/opening controls se hoga. Corrigendum/deadline extension authorised department user issue aur publish karta hai; ye automatic nahi hota, par material change ya insufficient time mein bidders ko fair response opportunity ke liye assess karein.

📘 Source: Corrigendum Issuance Manual (CHiPS)

## OPERATOR-05 — Department Operator — Pass

**Question:** Technical bids open kaise karte hain?

**Response time:** 12.93 seconds  
**Sources:** FInal_GFR_upto_31_07_2024.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf  
**Follow-ups:** What is the difference between technical and price bid? | Can I modify my bid after submission? | What happens if a corrigendum is issued?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Technical bids open karne ke liye, Ministry ya Department ko ek Consultancy Evaluation Committee (CEC) banani padti hai. Yeh committee technical bids ko open karti hai, aur phir unhe analyse aur evaluate karti hai. Committee ko har technical proposal ke acceptance ya rejection ke reasons detail mein record karne hote hain. Sirf unhi bidders ke financial bids open kiye jaate hain jinhe technically qualified declare kiya gaya ho.

📘 स्रोत: FInal_GFR_upto_31_07_2024, Manual_for_Procurement_of_works_2019, mannual procurement

## OPERATOR-06 — Department Operator — Pass

**Question:** Financial bids kab open karni chahiye?

**Response time:** 4.036 seconds  
**Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

💡 Answer
Original question “Financial bids kab open karni chahiye?” ko exact intent procurement_planning ke saath preserve kiya gaya hai. Is specific workflow ke liye reliable section available nahi hua, isliye kisi related lekin alag process ke steps nahi diye gaye hain. Relevant official section check karein.

## OPERATOR-07 — Department Operator — Pass

**Question:** Bid evaluation report generate kaise karte hain?

**Response time:** 9.474 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Bid evaluation report banane ka process tender ki financial value par depend karta hai. Agar tender ka value Rs. 50 lakhs se zyada hai, to ek Tender Committee banaya jaata hai jo bid ko evaluate karti hai. Yeh committee mein teen members hote hain, jisme ek finance member aur ek user department ka representative shaamil hota hai. Committee bid ko tender document ke terms and conditions ke basis par strictly evaluate karti hai. Evaluation transparent hona chahiye aur kisi bhi bidder ko undue advantage nahi milna chahiye. Report banane se pehle committee technical suitability report bhi maang sakti hai user departments se.

📘 Source: Manual for Procurement of Goods 2024

## OPERATOR-08 — Department Operator — Pass

**Question:** EMD refund initiate kaise karte hain department side se?

**Response time:** 2.568 seconds  
**Sources:** Online_EMD_Refund_Notice.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Answer
Applicable opening/evaluation stage ke baad Department Admin/Tender Owner eligible unsuccessful bidder ki EMD refund initiate karta hai. Department Approver verify aur approve karta hai; phir e-Procurement system registered bank account ke liye instruction bhejta hai. Completion ke liye portal status check karein. Fixed credit time promise na karein, kyunki approval aur bank processing vary karte hain.

📘 Source: EMD Refund Guidelines (CHiPS)

## OPERATOR-09 — Department Operator — Pass

**Question:** Offline tender upload karna ho to kya process hai?

**Response time:** 6.556 seconds  
**Sources:** Manual_Offline_Tenders_v.1.0.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Offline tender upload karne ke liye CHiPS e-Procurement portal par Tender Creator ke roop mein login karna padta hai. Iske liye step-by-step process yeh hai:

1.  **Login karein:** Portal par login karein aur 'Offline Tender' menu par click karein.
2.  **Header Details bharein:** 'MANUAL TENDER HEADER DETAIL' section mein saari jaankari bharein jaise TENDER NO., NIT REFERENCE NO, TENDER CALL NO, DETAILED DESCRIPTION, PROBABLE AMOUNT OF CONTRACT, Bid Submission Start date, Bid Open Date, aur TENDER & PROCESSING FEES. Phir 'SAVE' par click karein.
3.  **Payment karein:** 'Payment' par click karein, payment details enter karein aur 'SAVE' karein.
4.  **Evaluation mein Bidders add karein:** 'Evaluation' par click karein aur PAN No enter karke 'REGISTER NEW BIDDER' karein.
5.  **Bid Value enter karein:** Quoted/Bid Value aur Remarks enter karein aur 'SAVE' karein.
6.  **Finalize karein:** 'REGISTER' par click karein, phir 'Purchase Order' par click karke saare PO details aur attachments fill karein aur 'SAVE' karein.

📘 स्रोत: Manual_Offline_Tenders_v.1.0.pdf

## OPERATOR-10 — Department Operator — Pass

**Question:** Tender publish hone ke baad koi mistake mil jaye to kya karna chahiye?

**Response time:** 5.193 seconds  
**Sources:** publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Tender publish hone ke baad agar koi mistake milti hai, to uske liye corrigendum issue karna padta hai. Corrigendum ek amendment notice hota hai jo tender mein ki gayi galtiyon ya changes ko correct karne ke liye nikala jaata hai.

Iske liye ye steps follow karne hote hain:
1. Department Admin ya tender owner ko mistake identify karni padti hai.
2. Ek corrigendum draft kiya jaata hai jismein saaf likha hota hai ki kya correction ki ja rahi hai.
3. Corrigendum ko e-Procurement portal par upload kiya jaata hai.
4. Saare registered bidders ko corrigendum ka notification bheja jaata hai.

Corrigendum mein jo bhi changes hote hain, unhe sabhi bidders ke liye mandatory maana jaata hai. Agar koi bidder naye changes ke according bid submit nahi karta, to uski bid reject ho sakti hai.

📘 Source: Manual for Procurement of Goods 2024

## VENDOR-01 — Vendor / Bidder — Pass

**Question:** Main pehli baar government tender mein participate kar raha hoon. Kahan se shuru karun?

**Response time:** 17.247 seconds  
**Sources:** Store_Purhase_Rules_28.01.2021.pdf, publicProManual-1755343081262-715558279.pdf, Vigilance Manual (Updated 2021) English.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Pehli baar government tender mein participate karne ke liye aapko kuch basic steps follow karne honge. Main aapko process bata deta hoon:

**1. Vendor Registration:**
*   Sabse pehle aapko e-Procurement portal par vendor registration karna hoga. Yeh ek baar ki process hai.
*   Iske liye aapko valid DSC (Digital Signature Certificate) chahiye hoga.
*   Portal par "New Supplier Registration" ka option milega, wahan aap PAN card details aur zaroori documents upload karke submit karna hoga.

**2. Tender Dhundhna:**
*   e-Procurement portal par aapko active tenders dekh sakte hain.
*   Aap apni category ya zaroorat ke hisaab se tender filter kar sakte hain.

**3. Eligibility Check Karna:**
*   Har tender ke liye eligibility criteria hota hai. Aapko check karna hai ki aap un criteria ko meet karte hain ya nahi.
*   Ismein company type, turnover, experience, aur kisi bhi debarment ka record check hota hai.

**4. Tender Documents Download Karna:**
*   Jab aapko suitable tender mile, toh aap Notice Inviting Tender (NIT) aur baaki documents download kar sakte hain.
*   Yeh documents portal par downloadable form mein hote hain.

**5. Bidding Process:**
*   Aapko tender ke according technical bid aur price bid prepare karni hogi.
*   Technical bid mein aapka company ka detail aur capability batani hoti hai.
*   Price bid mein aap apni rates fill karte hain.

**6. Bid Submit Karna:**
*   Final bid submit karne ke liye aapko DSC use karna hoga.
*   Last date se pehle aap portal par bid upload karke submit kar dena hai.

**7. EMD (Earnest Money Deposit):**
*   Tender mein EMD bhi maanga jaata hai. Yeh refundable amount hota hai.
*   Aapko EMD challan ke through pay karna hoga.

**8. Performance Security:**
*   Agar aapka tender select hota hai, toh aapko performance security (bank guarantee ya FDR) bhi deni hogi.

Yeh process thoda detailed hai, lekin ek baar registration ho jaaye toh aage tenders participate karna easy ho jaata hai. Agar aapko koi specific step mein help chahiye, toh bataiye.

📘 स्रोत: Vendor Registration Manual (CHiPS)

## VENDOR-02 — Vendor / Bidder — Pass

**Question:** Vendor registration ka process kya hai?

**Response time:** 7.469 seconds  
**Sources:** CHiPS_Vendor_Registration_Manual_English.pdf  
**Follow-ups:** What documents are required for vendor registration? | How long does registration approval take? | Do I need a DSC to register?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Vendor registration ka process e-Procurement portal par online hota hai. Pehle aapko DSC lena padega. Foreign vendors ke liye DSC lene ka process thoda alag hai. Aapko licensed CAs se application form download karna hai aur documents ke saath Indian Embassy jaana hai. Wahan documents certified hote hain. Online fund transfer karna padta hai aur certified documents CA ko courier karne padte hain. Phir CA DSC aur e-token provide karta hai.

Existing suppliers ke liye Section 2 mein guide hai aur new suppliers ke liye Section 3 mein complete registration process di gayi hai. PWD registered suppliers ke liye alag Section 4 hai. Registration payment bhi karna padta hai jo Section 5 mein explain kiya gaya hai.

📘 स्रोत: Vendor Registration Manual (CHiPS)

## VENDOR-03 — Vendor / Bidder — Pass

**Question:** Registration ke liye kaun-kaun se documents chahiye?

**Response time:** 15.647 seconds  
**Sources:** GFR2017_HINDI.pdf, CHiPS_Vendor_Registration_Manual_English.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Vendor registration ke liye documents chahiye, jo do sources se mile hain:

**GFR 2017 ke according:**
- आपूर्तिकर्ता के प्रत्यय पत्र (credentials)
- विनिर्माण क्षमता (manufacturing capability)
- गुणवत्ता नियंत्रण प्रणाली (quality control system)
- विगत कार्यनिष्पादन (past performance)
- बिक्री बाद सेवा (after-sales service)
- वित्तीय पृष्ठभूमि (financial background)

**CHiPS Vendor Registration Manual ke according:**
**DSC के लिए:**
- Registration/Application form (licensed CAs से download करना है)
- Indian Embassy से certified true copies
- Online fund transfer (currency के according)

**Foreign vendors के लिए:**
इनमें से कोई भी एक document:
- Certificate of Incorporation
- Memorandum and Articles of Association
- Registered Partnership Deed
- Valid Business License document

**Registration process:**
1. Form download करें
2. Documents भरें और Indian Embassy जाएं
3. Embassy से certification करवाएं
4. Online payment करें
5. Documents CA को courier करें
6. CA से DSC प्राप्त करें

📘 स्रोत: GFR2017_HINDI, CHiPS_Vendor_Registration_Manual_English

## VENDOR-04 — Vendor / Bidder — Pass

**Question:** DSC map kaise karte hain?

**Response time:** 9.482 seconds  
**Sources:** CHiPS_Vendor_Registration_Manual_English.pdf  
**Follow-ups:** My DSC token is not recognised - what do I do? | Which class of DSC is required? | Can one DSC be used for multiple logins?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

DSC map karne ke liye pehle aapko ek DSC lena padega. Ye Class II ya Class III ka hona chahiye, aur usme Signing & Encryption dono certificates hone chahiye. Ye aapko kisi licensed CA se lena hoga.

DSC lene ke liye ye steps follow kijiye:

1.  **Form download kijiye:** Aap kisi bhi licensed CA se approved Registration/Application form download kijiye. Aap CCA ki website https://cca.gov.in par details dekh sakte hain.
2.  **Form bhariye aur documents jama kijiye:** Form ko bhariye aur zaroori documents ke saath Indian Embassy jaiye. Wahan original documents ke certified true copies submit kijiye.
3.  **Embassy se certification:** Embassy aapke documents ko certify karegi.
4.  **Online payment:** Aapko online fund transfer karna hoga. Amount Rupee mein equivalent hoga, jo respective country ki currency mein hoga. CA aapko Swift code provide karega.
5.  **Documents courier kijiye:** Embassy se certified documents ko courier karke CA ko bhejiye.
6.  **DSC receive kijiye:** CA aapko DSC aur e-token bhej dega.

Jab aapke paas DSC aa jaye, to aap e-Procurement portal par vendor registration kar sakte hain:

1.  Portal par registration details bhariye aur Save & Next kijiye.
2.  'Selecting DSC' step par aapko apna DSC select karna hoga. Ye certificate aapke Vendor/Bidder account ke saath register hona zaroori hai.
3.  DSC select karne ke baad, Confirmation par click karke Terms & Conditions accept kijiye.

📘 स्रोत: CHiPS_Vendor_Registration_Manual_English.pdf

## VENDOR-05 — Vendor / Bidder — Pass

**Question:** Bid submit karne ke baad usme changes kar sakte hain kya?

**Response time:** 5.639 seconds  
**Sources:** CHiPS_Bid_Submission_Manual_English.pdf  
**Follow-ups:** What is the difference between technical and price bid? | Can I modify my bid after submission? | What happens if a corrigendum is issued?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Context mein bid submit karne ke baad changes karne ke baare mein koi specific information nahi di gayi hai. Manual mein bid submission process ki details hain, jaise ki technical bid add karna aur documents attach karna, lekin submission ke baad modifications ke baare mein kuch nahi bataya gaya hai.

📘 स्रोत: CHiPS_Bid_Submission_Manual_English

## VENDOR-06 — Vendor / Bidder — Pass

**Question:** Deadline nikal gayi hai. Kya ab bhi bid edit ho sakti hai?

**Response time:** 10.933 seconds  
**Sources:** CHiPS_Bid_Submission_Manual_English.pdf, GFR2017_HINDI.pdf, Manual_for_Procurement_of_works_2019.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Deadline nikal gayi hai, toh bid edit karne ka chance bahut kam hai. Agar bid submission deadline pehle hi nikal gayi hai, toh bid edit nahi ho sakti.

Lekin, agar deadline extend hui hai toh:
- Agar e-Procurement system fail ho gaya tha (internet, power, server failure ya natural calamity), toh System Administrator Tender Inviting Authority se consult karke bid submission deadline extend kar sakta hai.
- Yeh extension 24, 48, ya 72 hours ka ho sakta hai.
- Iske liye ek Administrative Corrigendum issue kiya jaata hai aur affected bidders ko automatic email alert bhi jaata hai.

Agar deadline extend hui hai aur aapka time abhi bhi chal raha hai, toh aap bid edit kar sakte hain. Lekin agar deadline poori tarah nikal gayi hai, toh bid edit nahi ho sakti.

📘 स्रोत: CHiPS_Bid_Submission_Manual_English.pdf

## VENDOR-07 — Vendor / Bidder — Pass

**Question:** EMD ka payment kaise karna hota hai?

**Response time:** 16.739 seconds  
**Sources:** EMD_CHALLAN_PAYMENT_V1.0.pdf  
**Follow-ups:** When will my EMD be refunded? | Who is eligible for EMD exemption? | What is the difference between EMD and performance security?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

EMD ka payment karne ke do tarike hain - ek challan se aur doosra internet banking se.

**SECTION 1: EMD Payment via CHALLAN**
Challan se payment karne ke liye aapko Chhattisgarh e-Procurement portal par jaana hoga. Portal ka link hai: https://eprocdemo.cgstate.gov.in/CHEPS/security/getSignInAction.do

Yahan par aapko vendor ke credentials se login karna hoga. Login ke baad aap EMD payment ka option select kar sakte hain aur challan generate kar sakte hain.

**SECTION 2: EMD Payment via INTERNET BANKING**
Internet banking se payment karne ke liye bhi aapko e-Procurement portal par login karna hoga. Login ke baad EMD payment section mein jaakar aap direct internet banking se payment kar sakte hain.

Portal par aapko tender number, bid submission start date, bid due date aur probable amount of contract (PAC) ki details bhi bharni hongi.

📘 स्रोत: EMD Challan Payment Guide (CHiPS)

## VENDOR-08 — Vendor / Bidder — Pass

**Question:** Paisa account se kat gaya lekin EMD update nahi hua. Ab kya karun?

**Response time:** 15.167 seconds  
**Sources:** store purchase rule cg.pdf, GFR2017_HINDI.pdf, FInal_GFR_upto_31_07_2024.pdf  
**Follow-ups:** How do I pay EMD online? | When will my EMD be refunded? | What percentage of tender value is the EMD?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

EMD refund process ke liye, unsuccessful bidders ke liye Department Admin EMD refund initiate karta hai. Approval ke baad, e-Procurement system bank ko instruct karta hai aur amount 1-2 days mein credit ho jaata hai. Process typically Department Admin, phir Approver, aur finally bank ke through jaata hai.

Agar paisa account se kat gaya hai lekin EMD update nahi hua hai, toh aapko tender issuing department se contact karna chahiye. Unhe payment proof aur tender details provide karein. Department Admin ko refund process initiate karna hoga. Agar 15 days ke andar refund nahi milta hai, toh aap department se follow-up kar sakte hain.

📘 स्रोत: EMD Refund Guidelines (CHiPS)

## VENDOR-09 — Vendor / Bidder — Pass

**Question:** Agar meri bid reject ho gayi to EMD kab wapas milegi?

**Response time:** 8.108 seconds  
**Sources:** Online_EMD_Refund_Notice.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** How do I pay EMD online? | How long does the EMD refund take? | What if my bank account details changed?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Agar aapki bid reject ho gayi hai, to EMD refund process department officials dwara kiya jaata hai. CHiPS ka ismein koi intervention nahi hai. Refund process online e-Procurement system ke through hota hai, jismein payment gateway integrated hai. Department officials approval ke baad bank ko instruction dete hain, aur amount 1-2 days mein aapke account mein credit ho jaata hai.

📘 स्रोत: EMD Refund Guidelines (CHiPS)

## VENDOR-10 — Vendor / Bidder — Pass

**Question:** Corrigendum aaya hai ya nahi, kaise pata chalega?

**Response time:** 1.377 seconds  
**Sources:** GFRupdatedupto31012026.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Answer
Nahi. Corrigendum issue hone par deadline extension automatic nahi hota. Authorised department user assess kare ki change material hai ya bidders ko response revise karne ke liye time insufficient hai. Aisa ho to corrigendum publish karke level playing field ke liye adequate extension dein; warna no-extension ka reason record karein. Extension ko sirf system failure tak limit na karein.

📘 Source: General Financial Rules; Manual for Procurement of Goods 2024

## VENDOR-11 — Vendor / Bidder — Pass

**Question:** Reverse auction mein participate kaise karte hain?

**Response time:** 12.395 seconds  
**Sources:** AuctionManual_FA.pdf, CHiPS_Bid_Submission_Manual_English.pdf  
**Follow-ups:** How does reverse auction work? | How is EMD handled in auctions? | When is the auction EMD refunded?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Reverse auction mein participate karne ke liye aapko neeche diye gaye steps follow karne honge:

1.  **Portal Login:** Chhattisgarh e-Procurement portal https://eproc.cgstate.gov.in par login karein. Apna user-id, password, aur DSC use karein.
2.  **Auction Portal Access:** Dashboard par login karne ke baad, Auction tab par right-click karein aur "Open in new tab" select karein.
3.  **Password Change:** Agar auction engine password change karne ko kahe, to old password "Password@123" daalein aur naya password set karein.
4.  **Select Auction:** Auction dashboard se woh auction select karein jisme aap participate karna chahte hain aur "View/Respond to RFX" par click karein.
5.  **Accept Terms:** Auction terms accept karein.
6.  **Place Your Bid:** "Bid" par click karein. Aapki boli opening price se upar honi chahiye aur minimum bid change price ka multiple honi chahiye. Agar koi opening price nahi hai, to aap opening price ko '0' maan sakte hain.
7.  **Submit Bid:** Apni boli place karne ke baad "Submit Bid" button par click karein. Aap apni boli jitni chahein badha sakte hain, bas minimum bid change price ke multiple mein.

Auction ke dauran aap sirf H1 (highest) price aur ranking dekh paayenge. Auction page har 1 minute mein auto-refresh hoga.

📘 स्रोत: AuctionManual_FA.pdf

## VENDOR-12 — Vendor / Bidder — Pass

**Question:** Financial bid kab open hoti hai?

**Response time:** 14.584 seconds  
**Sources:** GFR2017_HINDI.pdf, Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf  
**Follow-ups:** What is the difference between technical and price bid? | Can I modify my bid after submission? | What happens if a corrigendum is issued?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Financial bid opening ke baare mein, Manual for Procurement of Works 2019 mein bataya gaya hai ki price bids technically suitable bidders ki presence mein open kiye jaate hain. Yeh ek pre-publicised date, time aur place par hota hai, ya phir e-procurement ke case mein portal par hota hai. Single envelope tender mein, tender committee CA ke reference ke bina price aspects ko evaluate karti hai.

📘 स्रोत: Manual for Procurement of Works 2019

## VENDOR-13 — Vendor / Bidder — Pass

**Question:** Startup company hoon. Kya government tender mein participate kar sakta hoon?

**Response time:** 2.463 seconds  
**Sources:** CHiPS_Bid_Submission_Manual_English.pdf, publicProManual-1755343081262-715558279.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Answer
Eligibility conditions tender mein stated, requirement se relevant aur sab par equally applied honi chahiye. Turnover, experience, local support, MSME/startup benefit, land-border restriction aur documents sirf applicable rule/tender ki scope aur required evidence ke according apply hote hain. Ye automatic waiver ya arbitrary restriction nahi hain. Publication ke baad ek bidder ke liye material criterion relax na karein; permitted change ho to common corrigendum aur material change par adequate time dein.

📘 Source: Bid Submission Manual (CHiPS); Manual for Procurement of Goods 2024

## VENDOR-14 — Vendor / Bidder — Pass

**Question:** Foreign company bhi Chhattisgarh tender mein participate kar sakti hai kya?

**Response time:** 9.403 seconds  
**Sources:** CHiPS_Vendor_Registration_Manual_English.pdf  
**Follow-ups:** None  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Answer
Pehle specific Tender mein foreign-bidder participation, eligibility, currency aur registration conditions check karein. DSC ke liye licensed Certificate Authority se application lein, required organisation/identity documents complete karein, applicable process mein Indian Embassy certification karayein, prescribed documents/payment CA ko submit karein aur DSC/e-token obtain karein. Tender ki eligibility aur registration conditions hi final control karengi.

📘 Source: Vendor Registration Manual (CHiPS)

## VENDOR-15 — Vendor / Bidder — Pass

**Question:** Bid submit karne ke baad acknowledgement kahan milega?

**Response time:** 9.192 seconds  
**Sources:** CHiPS_Bid_Submission_Manual_English.pdf  
**Follow-ups:** What changes if the estimated value is below ₹3 lakh? | Does GeM have to be checked before inviting a tender? | What approval, publication, and timeline apply?  
**Checks:** answer=True, source=True, provider/transport error=False

### Chatbot response

Bid submit karne ke baad acknowledgement milne ke liye, aapko e-Procurement portal par login karna hoga. Login karne ke baad, aap apne "Tenders" section mein ja sakte hain. Wahan aapko "Bidding" ya "Bid Submission" ka option milega, jahan aap apni submitted bids ki status check kar sakte hain. Acknowledgement ya confirmation usually bid submission ke baad automatically generate hota hai aur portal par dikhta hai.

📘 स्रोत: CHiPS_Bid_Submission_Manual_English
