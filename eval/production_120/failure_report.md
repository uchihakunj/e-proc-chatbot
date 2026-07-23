# Failure-only report

Non-pass cases: 92/120

## fallback (58)

- Q3 [Fail]: We need printers for the government office; what should we do first? — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=False; final=False
- Q9 [Fail]: Can our department purchase a printer directly from GeM? — actor department_buyer→department_buyer; intent gem_direct_purchase_rule→gem_department_purchase_process; top5=True; final=True
- Q11 [Fail]: What budget and administrative approvals are needed before a department purchase? — actor department_buyer→department_buyer; intent approval_and_budget→approval_and_budget; top5=True; final=True
- Q18 [Fail]: Supplier ko payment aur asset register entry ka workflow kya hai? — actor department_buyer→general_information_user; intent payment_and_asset_entry→payment_and_asset_entry; top5=True; final=True
- Q19 [Fail]: GeM par L1 purchase department kaise kare? — actor department_buyer→department_buyer; intent gem_l1_purchase→gem_department_purchase_process; top5=True; final=True
- Q20 [Partial]: Department ko GeM bidding se computer kharidne hain, kya process hai? — actor department_buyer→department_buyer; intent gem_department_purchase_process→gem_department_purchase_process; top5=True; final=True
- Q21 [Partial]: GeM reverse auction department kab use kare? — actor department_buyer→department_buyer; intent gem_reverse_auction→gem_reverse_auction; top5=True; final=True
- Q25 [Fail]: प्रिंटर की तकनीकी विनिर्देश निष्पक्ष रूप से कैसे तैयार करें? — actor department_buyer→department_buyer; intent specification_preparation→specification_preparation; top5=True; final=True
- Q27 [Fail]: बोली मूल्यांकन के बाद क्रय आदेश जारी करने की प्रक्रिया क्या है? — actor department_buyer→general_information_user; intent purchase_order→purchase_order; top5=True; final=True
- Q32 [Partial]: Which documents are required for new supplier registration? — actor vendor_bidder→vendor_bidder; intent vendor_registration_documents→vendor_registration_documents; top5=True; final=True
- Q34 [Fail]: I forgot my vendor login password. How can I reset it? — actor vendor_bidder→general_information_user; intent password_recovery→password_recovery; top5=True; final=True
- Q35 [Fail]: As a bidder, how do I obtain a DSC? — actor vendor_bidder→vendor_bidder; intent dsc_obtainment→dsc_obtainment; top5=True; final=True
- Q36 [Partial]: How do I map my renewed DSC on the e-procurement portal? — actor vendor_bidder→vendor_bidder; intent dsc_mapping→dsc_mapping; top5=True; final=True
- Q38 [Partial]: My EMD payment failed but the amount was debited. What next? — actor vendor_bidder→vendor_bidder; intent emd_payment_failure→emd_payment_failure; top5=True; final=True
- Q41 [Fail]: Am I eligible to participate in this government tender? — actor vendor_bidder→general_information_user; intent tender_eligibility→unknown; top5=False; final=False
- Q43 [Fail]: Vendor registrtion ke liye kya dokuments lagenge? — actor vendor_bidder→general_information_user; intent vendor_registration_documents→unknown; top5=True; final=True
- Q44 [Partial]: Mera vendor password bhool gaya, reset kaise hoga? — actor vendor_bidder→vendor_bidder; intent password_recovery→password_recovery; top5=True; final=True
- Q45 [Partial]: Bidder DSC token ko portal se map kaise kare? — actor vendor_bidder→vendor_bidder; intent dsc_mapping→dsc_mapping; top5=True; final=True
- Q47 [Fail]: EMD 2 lakh jama karni hai 30 July 2026 tak, steps batao. — actor vendor_bidder→general_information_user; intent emd_payment→emd_payment; top5=True; final=True
- Q49 [Partial]: L1 bidder ki EMD ka kya hota hai? — actor vendor_bidder→vendor_bidder; intent emd_refund_l1_bidder→emd_refund_l1_bidder; top5=True; final=True
- Q50 [Fail]: Tender me bid submit kaise karu? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q53 [Fail]: Reverse auction mein vendor kaise participate kare? — actor vendor_bidder→general_information_user; intent auction_participation→unknown; top5=True; final=True
- Q54 [Fail]: मैं नया विक्रेता हूँ। पोर्टल पर पंजीकरण कैसे करूँ? — actor vendor_bidder→general_information_user; intent vendor_registration→unknown; top5=True; final=True
- Q55 [Fail]: बोलीदाता अपना डिजिटल हस्ताक्षर प्रमाणपत्र कैसे जोड़े? — actor vendor_bidder→general_information_user; intent dsc_mapping→dsc_mapping; top5=True; final=True
- Q56 [Fail]: मुझे ईएमडी जमा करनी है। ऑनलाइन भुगतान प्रक्रिया बताइए। — actor vendor_bidder→general_information_user; intent emd_payment→payment_and_asset_entry; top5=False; final=False
- Q58 [Fail]: तकनीकी और मूल्य बोली ऑनलाइन कैसे जमा करें? — actor vendor_bidder→general_information_user; intent bid_submission_portal_steps→unknown; top5=False; final=False
- Q59 [Fail]: शुद्धिपत्र आने पर मेरी जमा बोली का क्या होगा? — actor vendor_bidder→general_information_user; intent bid_deletion_after_corrigendum→corrigendum_policy; top5=False; final=False
- Q60 [Fail]: ई-नीलामी में बोलीदाता कैसे भाग ले? — actor vendor_bidder→general_information_user; intent auction_participation→unknown; top5=True; final=True
- Q62 [Fail]: How does the tender owner publish a completed tender? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q65 [Fail]: How does a tender owner issue an EMD/Bid Security Corrigendum? — actor department_operator→department_operator; intent corrigendum_portal_steps→emd_definition; top5=False; final=False
- Q66 [Partial]: How should the bid opener open the technical bid online? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q67 [Partial]: How does the department operator open the price bid? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q69 [Fail]: How can an operator upload and publish an offline tender? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=True; final=True
- Q70 [Partial]: Tender owner portal par naya tender create kaise kare? — actor department_operator→department_operator; intent tender_creation_portal_steps→tender_creation_portal_steps; top5=True; final=True
- Q71 [Fail]: Department operator tender publish kaise kare? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q73 [Fail]: Tender term corrigendum kaise jari kare department user? — actor department_operator→department_buyer; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q74 [Fail]: Attachment corrigendum upload aur publish kaise hoga? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q75 [Fail]: Required attachment corrigendum me bid deletion option kya kare? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q79 [Fail]: विभागीय ऑपरेटर पोर्टल पर निविदा कैसे बनाए? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=False; final=False
- Q80 [Fail]: निविदा स्वामी निविदा प्रकाशित कैसे करे? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q81 [Fail]: विभागीय उपयोगकर्ता ईएमडी शुद्धिपत्र कैसे जारी करे? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q82 [Fail]: आइटम शुद्धिपत्र जारी करने की पोर्टल प्रक्रिया बताइए। — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q83 [Partial]: तकनीकी बोली खोलने की ऑनलाइन प्रक्रिया क्या है? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q85 [Fail]: ऑफलाइन निविदा को पोर्टल पर अपलोड और प्रकाशित कैसे करें? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=False; final=False
- Q87 [Fail]: What is GeM? — actor general_information_user→general_information_user; intent gem_definition→gem_definition; top5=True; final=True
- Q95 [Fail]: CG me govt procurement ke alag tarike kya hain? — actor general_information_user→general_information_user; intent procurement_methods_overview→procurement_methods_overview; top5=True; final=True
- Q96 [Fail]: GeM kya hota hai? — actor general_information_user→general_information_user; intent gem_definition→gem_definition; top5=True; final=True
- Q97 [Fail]: GeM aur state e-procurement portal me fark batao. — actor general_information_user→general_information_user; intent gem_eproc_comparison→gem_definition; top5=True; final=True
- Q101 [Fail]: EMD kya hai aur kyu li jati hai? — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=False; final=False
- Q105 [Fail]: जेम क्या है? — actor general_information_user→general_information_user; intent gem_definition→unknown; top5=False; final=False
- Q106 [Fail]: जेम और छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल में क्या अंतर है? — actor general_information_user→general_information_user; intent gem_eproc_comparison→unknown; top5=True; final=False
- Q110 [Fail]: शुद्धिपत्र का कानूनी उद्देश्य क्या है? — actor general_information_user→general_information_user; intent corrigendum_policy→corrigendum_policy; top5=True; final=True
- Q112 [Fail]: What is the EMD process? — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=True; final=True
- Q116 [Fail]: Tender banana hai ya bid bharni hai, kya karu? — actor general_information_user→general_information_user; intent mixed_role_clarification→tender_creation_policy; top5=True; final=False
- Q117 [Fail]: EMD ka process short me batao. — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=False; final=False
- Q118 [Fail]: Corrigendum kaise hota hai? — actor general_information_user→general_information_user; intent corrigendum_policy→corrigendum_policy; top5=True; final=True
- Q119 [Fail]: मुझे प्रिंटर खरीदने की प्रक्रिया बताइए। — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=True; final=True
- Q120 [Fail]: निविदा बनानी है या बोली जमा करनी है? — actor general_information_user→general_information_user; intent mixed_role_clarification→unknown; top5=False; final=False

Likely files: 05_webui/fine_intent_policy.py; 05_webui/actor_boundary.py

Minimal fix: Determine whether the fallback is caused by missing evidence or a rejected grounded draft before changing fallback text.

Risk: Medium-high: fallback logic is already verified.

## actor classification (38)

- Q3 [Fail]: We need printers for the government office; what should we do first? — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=False; final=False
- Q16 [Fail]: Bid evaluation ke baad purchase order issue karne ka process batao. — actor department_buyer→general_information_user; intent purchase_order→bid_evaluation; top5=True; final=True
- Q18 [Fail]: Supplier ko payment aur asset register entry ka workflow kya hai? — actor department_buyer→general_information_user; intent payment_and_asset_entry→payment_and_asset_entry; top5=True; final=True
- Q26 [Fail]: विभागीय खरीद से पहले बजट और प्रशासनिक स्वीकृति कैसे लें? — actor department_buyer→general_information_user; intent approval_and_budget→inspection_and_acceptance; top5=True; final=True
- Q27 [Fail]: बोली मूल्यांकन के बाद क्रय आदेश जारी करने की प्रक्रिया क्या है? — actor department_buyer→general_information_user; intent purchase_order→purchase_order; top5=True; final=True
- Q28 [Fail]: आपूर्ति मिलने पर निरीक्षण और स्वीकृति कैसे की जाए? — actor department_buyer→general_information_user; intent inspection_and_acceptance→inspection_and_acceptance; top5=True; final=True
- Q29 [Fail]: भुगतान के बाद स्टॉक और संपत्ति रजिस्टर में प्रविष्टि कैसे करें? — actor department_buyer→general_information_user; intent payment_and_asset_entry→payment_and_asset_entry; top5=True; final=True
- Q31 [Fail]: How do I register as a new vendor on the portal? — actor vendor_bidder→general_information_user; intent vendor_registration→unknown; top5=True; final=True
- Q34 [Fail]: I forgot my vendor login password. How can I reset it? — actor vendor_bidder→general_information_user; intent password_recovery→password_recovery; top5=True; final=True
- Q40 [Fail]: How can I submit my technical and price bid online? — actor vendor_bidder→general_information_user; intent bid_submission_portal_steps→unknown; top5=True; final=False
- Q41 [Fail]: Am I eligible to participate in this government tender? — actor vendor_bidder→general_information_user; intent tender_eligibility→unknown; top5=False; final=False
- Q43 [Fail]: Vendor registrtion ke liye kya dokuments lagenge? — actor vendor_bidder→general_information_user; intent vendor_registration_documents→unknown; top5=True; final=True
- Q47 [Fail]: EMD 2 lakh jama karni hai 30 July 2026 tak, steps batao. — actor vendor_bidder→general_information_user; intent emd_payment→emd_payment; top5=True; final=True
- Q53 [Fail]: Reverse auction mein vendor kaise participate kare? — actor vendor_bidder→general_information_user; intent auction_participation→unknown; top5=True; final=True
- Q54 [Fail]: मैं नया विक्रेता हूँ। पोर्टल पर पंजीकरण कैसे करूँ? — actor vendor_bidder→general_information_user; intent vendor_registration→unknown; top5=True; final=True
- Q55 [Fail]: बोलीदाता अपना डिजिटल हस्ताक्षर प्रमाणपत्र कैसे जोड़े? — actor vendor_bidder→general_information_user; intent dsc_mapping→dsc_mapping; top5=True; final=True
- Q56 [Fail]: मुझे ईएमडी जमा करनी है। ऑनलाइन भुगतान प्रक्रिया बताइए। — actor vendor_bidder→general_information_user; intent emd_payment→payment_and_asset_entry; top5=False; final=False
- Q57 [Fail]: असफल बोलीदाता की ईएमडी वापसी कैसे होती है? — actor vendor_bidder→general_information_user; intent emd_refund_unsuccessful_bidder→unknown; top5=True; final=True
- Q58 [Fail]: तकनीकी और मूल्य बोली ऑनलाइन कैसे जमा करें? — actor vendor_bidder→general_information_user; intent bid_submission_portal_steps→unknown; top5=False; final=False
- Q59 [Fail]: शुद्धिपत्र आने पर मेरी जमा बोली का क्या होगा? — actor vendor_bidder→general_information_user; intent bid_deletion_after_corrigendum→corrigendum_policy; top5=False; final=False
- Q60 [Fail]: ई-नीलामी में बोलीदाता कैसे भाग ले? — actor vendor_bidder→general_information_user; intent auction_participation→unknown; top5=True; final=True
- Q64 [Fail]: Give the portal steps for issuing a Date Corrigendum. — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_portal_steps; top5=True; final=True
- Q68 [Fail]: How do department users process bidders' EMD refunds? — actor department_operator→vendor_bidder; intent emd_remittance_to_department→emd_refund_unsuccessful_bidder; top5=True; final=True
- Q69 [Fail]: How can an operator upload and publish an offline tender? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=True; final=True
- Q72 [Fail]: Date corrigendum portal par issue karne ke steps? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_portal_steps; top5=True; final=True
- Q73 [Fail]: Tender term corrigendum kaise jari kare department user? — actor department_operator→department_buyer; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q74 [Fail]: Attachment corrigendum upload aur publish kaise hoga? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q75 [Fail]: Required attachment corrigendum me bid deletion option kya kare? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q76 [Fail]: Technical bid open karne ka operator workflow batao. — actor department_operator→general_information_user; intent bid_opening_portal_steps→unknown; top5=False; final=False
- Q77 [Fail]: Department approver EMD refund process kaise complete kare? — actor department_operator→vendor_bidder; intent emd_remittance_to_department→emd_remittance_to_department; top5=True; final=True
- Q78 [Fail]: Offline tendr portal pe upload kaise karna hai? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=True; final=True
- Q79 [Fail]: विभागीय ऑपरेटर पोर्टल पर निविदा कैसे बनाए? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=False; final=False
- Q81 [Fail]: विभागीय उपयोगकर्ता ईएमडी शुद्धिपत्र कैसे जारी करे? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q82 [Fail]: आइटम शुद्धिपत्र जारी करने की पोर्टल प्रक्रिया बताइए। — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q84 [Fail]: विभाग असफल बोलीदाताओं की ईएमडी वापसी कैसे संसाधित करे? — actor department_operator→department_buyer; intent emd_remittance_to_department→procurement_planning; top5=False; final=False
- Q85 [Fail]: ऑफलाइन निविदा को पोर्टल पर अपलोड और प्रकाशित कैसे करें? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=False; final=False
- Q113 [Fail]: Should I create a tender or submit a bid? — actor general_information_user→department_operator; intent mixed_role_clarification→tender_creation_portal_steps; top5=True; final=True
- Q119 [Fail]: मुझे प्रिंटर खरीदने की प्रक्रिया बताइए। — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=True; final=True

Likely files: 05_webui/actor_policy.py; 05_webui/nlp_features.py

Minimal fix: Add only the failing phrase to the narrow actor signal/rule and add its regression case.

Risk: High: actor changes affect retrieval and generation.

## generation (35)

- Q9 [Fail]: Can our department purchase a printer directly from GeM? — actor department_buyer→department_buyer; intent gem_direct_purchase_rule→gem_department_purchase_process; top5=True; final=True
- Q11 [Fail]: What budget and administrative approvals are needed before a department purchase? — actor department_buyer→department_buyer; intent approval_and_budget→approval_and_budget; top5=True; final=True
- Q13 [Fail]: Department ke liye printer ki specifications kaise banayein? — actor department_buyer→department_buyer; intent specification_preparation→specification_preparation; top5=True; final=True
- Q14 [Fail]: Hamare office ko open tender se furniture lena hai, planning kya hogi? — actor department_buyer→department_buyer; intent procurement_planning→tender_method_definition; top5=True; final=True
- Q16 [Fail]: Bid evaluation ke baad purchase order issue karne ka process batao. — actor department_buyer→general_information_user; intent purchase_order→bid_evaluation; top5=True; final=True
- Q17 [Fail]: PO ke baad maal ka inspection aur acceptance kaise karein? — actor department_buyer→department_buyer; intent inspection_and_acceptance→inspection_and_acceptance; top5=True; final=True
- Q18 [Fail]: Supplier ko payment aur asset register entry ka workflow kya hai? — actor department_buyer→general_information_user; intent payment_and_asset_entry→payment_and_asset_entry; top5=True; final=True
- Q19 [Fail]: GeM par L1 purchase department kaise kare? — actor department_buyer→department_buyer; intent gem_l1_purchase→gem_department_purchase_process; top5=True; final=True
- Q25 [Fail]: प्रिंटर की तकनीकी विनिर्देश निष्पक्ष रूप से कैसे तैयार करें? — actor department_buyer→department_buyer; intent specification_preparation→specification_preparation; top5=True; final=True
- Q26 [Fail]: विभागीय खरीद से पहले बजट और प्रशासनिक स्वीकृति कैसे लें? — actor department_buyer→general_information_user; intent approval_and_budget→inspection_and_acceptance; top5=True; final=True
- Q27 [Fail]: बोली मूल्यांकन के बाद क्रय आदेश जारी करने की प्रक्रिया क्या है? — actor department_buyer→general_information_user; intent purchase_order→purchase_order; top5=True; final=True
- Q29 [Fail]: भुगतान के बाद स्टॉक और संपत्ति रजिस्टर में प्रविष्टि कैसे करें? — actor department_buyer→general_information_user; intent payment_and_asset_entry→payment_and_asset_entry; top5=True; final=True
- Q35 [Fail]: As a bidder, how do I obtain a DSC? — actor vendor_bidder→vendor_bidder; intent dsc_obtainment→dsc_obtainment; top5=True; final=True
- Q46 [Fail]: Renewed DSC se login nahi ho raha, kya karun? — actor vendor_bidder→vendor_bidder; intent dsc_login_problem→dsc_login_problem; top5=True; final=True
- Q47 [Fail]: EMD 2 lakh jama karni hai 30 July 2026 tak, steps batao. — actor vendor_bidder→general_information_user; intent emd_payment→emd_payment; top5=True; final=True
- Q50 [Fail]: Tender me bid submit kaise karu? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q51 [Fail]: Submitted bid ko deadline se pehle modify aur resubmit kaise karein? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q53 [Fail]: Reverse auction mein vendor kaise participate kare? — actor vendor_bidder→general_information_user; intent auction_participation→unknown; top5=True; final=True
- Q63 [Fail]: How does a department issue a corrigendum on the portal? — actor department_operator→department_operator; intent corrigendum_portal_steps→corrigendum_portal_steps; top5=True; final=True
- Q64 [Fail]: Give the portal steps for issuing a Date Corrigendum. — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_portal_steps; top5=True; final=True
- Q69 [Fail]: How can an operator upload and publish an offline tender? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=True; final=True
- Q72 [Fail]: Date corrigendum portal par issue karne ke steps? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_portal_steps; top5=True; final=True
- Q87 [Fail]: What is GeM? — actor general_information_user→general_information_user; intent gem_definition→gem_definition; top5=True; final=True
- Q90 [Fail]: What is a single tender and when is it exceptional? — actor general_information_user→general_information_user; intent tender_method_definition→tender_method_definition; top5=True; final=True
- Q94 [Fail]: What do the Chhattisgarh Store Purchase Rules govern? — actor general_information_user→general_information_user; intent procurement_methods_overview→unknown; top5=True; final=True
- Q95 [Fail]: CG me govt procurement ke alag tarike kya hain? — actor general_information_user→general_information_user; intent procurement_methods_overview→procurement_methods_overview; top5=True; final=True
- Q96 [Fail]: GeM kya hota hai? — actor general_information_user→general_information_user; intent gem_definition→gem_definition; top5=True; final=True
- Q97 [Fail]: GeM aur state e-procurement portal me fark batao. — actor general_information_user→general_information_user; intent gem_eproc_comparison→gem_definition; top5=True; final=True
- Q100 [Fail]: Open tender sab vendors ke liye hota hai kya? — actor general_information_user→general_information_user; intent tender_method_definition→tender_method_definition; top5=True; final=True
- Q103 [Fail]: Store Purchase Rules CG kis purchase par apply hote hain? — actor general_information_user→general_information_user; intent procurement_methods_overview→unknown; top5=True; final=True
- Q108 [Fail]: एकल निविदा क्या है और इसका उपयोग कब होता है? — actor general_information_user→general_information_user; intent tender_method_definition→tender_method_definition; top5=True; final=True
- Q110 [Fail]: शुद्धिपत्र का कानूनी उद्देश्य क्या है? — actor general_information_user→general_information_user; intent corrigendum_policy→corrigendum_policy; top5=True; final=True
- Q112 [Fail]: What is the EMD process? — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=True; final=True
- Q118 [Fail]: Corrigendum kaise hota hai? — actor general_information_user→general_information_user; intent corrigendum_policy→corrigendum_policy; top5=True; final=True
- Q119 [Fail]: मुझे प्रिंटर खरीदने की प्रक्रिया बताइए। — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=True; final=True

Likely files: 05_webui/app.py; 05_webui/fine_intent_policy.py

Minimal fix: Tighten the intent-specific evidence/answer contract; do not add an unrelated synthetic workflow.

Risk: Medium: stronger guards can increase fallback use.

## citation (30)

- Q3 [Fail]: We need printers for the government office; what should we do first? — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=False; final=False
- Q40 [Fail]: How can I submit my technical and price bid online? — actor vendor_bidder→general_information_user; intent bid_submission_portal_steps→unknown; top5=True; final=False
- Q41 [Fail]: Am I eligible to participate in this government tender? — actor vendor_bidder→general_information_user; intent tender_eligibility→unknown; top5=False; final=False
- Q56 [Fail]: मुझे ईएमडी जमा करनी है। ऑनलाइन भुगतान प्रक्रिया बताइए। — actor vendor_bidder→general_information_user; intent emd_payment→payment_and_asset_entry; top5=False; final=False
- Q58 [Fail]: तकनीकी और मूल्य बोली ऑनलाइन कैसे जमा करें? — actor vendor_bidder→general_information_user; intent bid_submission_portal_steps→unknown; top5=False; final=False
- Q59 [Fail]: शुद्धिपत्र आने पर मेरी जमा बोली का क्या होगा? — actor vendor_bidder→general_information_user; intent bid_deletion_after_corrigendum→corrigendum_policy; top5=False; final=False
- Q62 [Fail]: How does the tender owner publish a completed tender? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q65 [Fail]: How does a tender owner issue an EMD/Bid Security Corrigendum? — actor department_operator→department_operator; intent corrigendum_portal_steps→emd_definition; top5=False; final=False
- Q66 [Partial]: How should the bid opener open the technical bid online? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q67 [Partial]: How does the department operator open the price bid? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q71 [Fail]: Department operator tender publish kaise kare? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q73 [Fail]: Tender term corrigendum kaise jari kare department user? — actor department_operator→department_buyer; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q74 [Fail]: Attachment corrigendum upload aur publish kaise hoga? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q75 [Fail]: Required attachment corrigendum me bid deletion option kya kare? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q76 [Fail]: Technical bid open karne ka operator workflow batao. — actor department_operator→general_information_user; intent bid_opening_portal_steps→unknown; top5=False; final=False
- Q79 [Fail]: विभागीय ऑपरेटर पोर्टल पर निविदा कैसे बनाए? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=False; final=False
- Q80 [Fail]: निविदा स्वामी निविदा प्रकाशित कैसे करे? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q81 [Fail]: विभागीय उपयोगकर्ता ईएमडी शुद्धिपत्र कैसे जारी करे? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q82 [Fail]: आइटम शुद्धिपत्र जारी करने की पोर्टल प्रक्रिया बताइए। — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q83 [Partial]: तकनीकी बोली खोलने की ऑनलाइन प्रक्रिया क्या है? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q84 [Fail]: विभाग असफल बोलीदाताओं की ईएमडी वापसी कैसे संसाधित करे? — actor department_operator→department_buyer; intent emd_remittance_to_department→procurement_planning; top5=False; final=False
- Q85 [Fail]: ऑफलाइन निविदा को पोर्टल पर अपलोड और प्रकाशित कैसे करें? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=False; final=False
- Q91 [Fail]: What does open tender mean? — actor general_information_user→general_information_user; intent tender_method_definition→unknown; top5=False; final=False
- Q99 [Fail]: Single tender kab allowed hota hai? — actor general_information_user→general_information_user; intent tender_method_definition→unknown; top5=True; final=False
- Q101 [Fail]: EMD kya hai aur kyu li jati hai? — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=False; final=False
- Q105 [Fail]: जेम क्या है? — actor general_information_user→general_information_user; intent gem_definition→unknown; top5=False; final=False
- Q106 [Fail]: जेम और छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल में क्या अंतर है? — actor general_information_user→general_information_user; intent gem_eproc_comparison→unknown; top5=True; final=False
- Q116 [Fail]: Tender banana hai ya bid bharni hai, kya karu? — actor general_information_user→general_information_user; intent mixed_role_clarification→tender_creation_policy; top5=True; final=False
- Q117 [Fail]: EMD ka process short me batao. — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=False; final=False
- Q120 [Fail]: निविदा बनानी है या बोली जमा करनी है? — actor general_information_user→general_information_user; intent mixed_role_clarification→unknown; top5=False; final=False

Likely files: 05_webui/app.py; 05_webui/static/script.js

Minimal fix: Keep final source IDs aligned with selected context and rendered source links.

Risk: Low if source normalization is isolated.

## procedural completeness (28)

- Q3 [Fail]: We need printers for the government office; what should we do first? — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=False; final=False
- Q11 [Fail]: What budget and administrative approvals are needed before a department purchase? — actor department_buyer→department_buyer; intent approval_and_budget→approval_and_budget; top5=True; final=True
- Q13 [Fail]: Department ke liye printer ki specifications kaise banayein? — actor department_buyer→department_buyer; intent specification_preparation→specification_preparation; top5=True; final=True
- Q14 [Fail]: Hamare office ko open tender se furniture lena hai, planning kya hogi? — actor department_buyer→department_buyer; intent procurement_planning→tender_method_definition; top5=True; final=True
- Q16 [Fail]: Bid evaluation ke baad purchase order issue karne ka process batao. — actor department_buyer→general_information_user; intent purchase_order→bid_evaluation; top5=True; final=True
- Q17 [Fail]: PO ke baad maal ka inspection aur acceptance kaise karein? — actor department_buyer→department_buyer; intent inspection_and_acceptance→inspection_and_acceptance; top5=True; final=True
- Q18 [Fail]: Supplier ko payment aur asset register entry ka workflow kya hai? — actor department_buyer→general_information_user; intent payment_and_asset_entry→payment_and_asset_entry; top5=True; final=True
- Q25 [Fail]: प्रिंटर की तकनीकी विनिर्देश निष्पक्ष रूप से कैसे तैयार करें? — actor department_buyer→department_buyer; intent specification_preparation→specification_preparation; top5=True; final=True
- Q26 [Fail]: विभागीय खरीद से पहले बजट और प्रशासनिक स्वीकृति कैसे लें? — actor department_buyer→general_information_user; intent approval_and_budget→inspection_and_acceptance; top5=True; final=True
- Q27 [Fail]: बोली मूल्यांकन के बाद क्रय आदेश जारी करने की प्रक्रिया क्या है? — actor department_buyer→general_information_user; intent purchase_order→purchase_order; top5=True; final=True
- Q29 [Fail]: भुगतान के बाद स्टॉक और संपत्ति रजिस्टर में प्रविष्टि कैसे करें? — actor department_buyer→general_information_user; intent payment_and_asset_entry→payment_and_asset_entry; top5=True; final=True
- Q35 [Fail]: As a bidder, how do I obtain a DSC? — actor vendor_bidder→vendor_bidder; intent dsc_obtainment→dsc_obtainment; top5=True; final=True
- Q46 [Fail]: Renewed DSC se login nahi ho raha, kya karun? — actor vendor_bidder→vendor_bidder; intent dsc_login_problem→dsc_login_problem; top5=True; final=True
- Q47 [Fail]: EMD 2 lakh jama karni hai 30 July 2026 tak, steps batao. — actor vendor_bidder→general_information_user; intent emd_payment→emd_payment; top5=True; final=True
- Q50 [Fail]: Tender me bid submit kaise karu? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q51 [Fail]: Submitted bid ko deadline se pehle modify aur resubmit kaise karein? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q53 [Fail]: Reverse auction mein vendor kaise participate kare? — actor vendor_bidder→general_information_user; intent auction_participation→unknown; top5=True; final=True
- Q56 [Fail]: मुझे ईएमडी जमा करनी है। ऑनलाइन भुगतान प्रक्रिया बताइए। — actor vendor_bidder→general_information_user; intent emd_payment→payment_and_asset_entry; top5=False; final=False
- Q62 [Fail]: How does the tender owner publish a completed tender? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q65 [Fail]: How does a tender owner issue an EMD/Bid Security Corrigendum? — actor department_operator→department_operator; intent corrigendum_portal_steps→emd_definition; top5=False; final=False
- Q69 [Fail]: How can an operator upload and publish an offline tender? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=True; final=True
- Q71 [Fail]: Department operator tender publish kaise kare? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q73 [Fail]: Tender term corrigendum kaise jari kare department user? — actor department_operator→department_buyer; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q74 [Fail]: Attachment corrigendum upload aur publish kaise hoga? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q75 [Fail]: Required attachment corrigendum me bid deletion option kya kare? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q80 [Fail]: निविदा स्वामी निविदा प्रकाशित कैसे करे? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q81 [Fail]: विभागीय उपयोगकर्ता ईएमडी शुद्धिपत्र कैसे जारी करे? — actor department_operator→general_information_user; intent corrigendum_portal_steps→corrigendum_policy; top5=False; final=False
- Q119 [Fail]: मुझे प्रिंटर खरीदने की प्रक्रिया बताइए। — actor department_buyer→general_information_user; intent procurement_planning→unknown; top5=True; final=True

Likely files: 05_webui/fine_intent_policy.py; 05_webui/app.py

Minimal fix: Require the missing in-scope stages only for this procedural intent.

Risk: Low-medium if limited to one intent.

## fine-intent classification (27)

- Q8 [Partial]: Which purchase method should our department choose during an emergency? — actor department_buyer→department_buyer; intent procurement_method_selection→procurement_planning; top5=True; final=True
- Q9 [Fail]: Can our department purchase a printer directly from GeM? — actor department_buyer→department_buyer; intent gem_direct_purchase_rule→gem_department_purchase_process; top5=True; final=True
- Q12 [Partial]: How should the department evaluate technical and financial bids? — actor department_buyer→department_buyer; intent bid_evaluation→procurement_planning; top5=False; final=True
- Q14 [Fail]: Hamare office ko open tender se furniture lena hai, planning kya hogi? — actor department_buyer→department_buyer; intent procurement_planning→tender_method_definition; top5=True; final=True
- Q15 [Partial]: Limited tender kab choose kare department buyer? — actor department_buyer→department_buyer; intent procurement_method_selection→procurement_planning; top5=True; final=True
- Q19 [Fail]: GeM par L1 purchase department kaise kare? — actor department_buyer→department_buyer; intent gem_l1_purchase→gem_department_purchase_process; top5=True; final=True
- Q30 [Partial]: आपातकाल में विभाग को तुरंत सामान खरीदना हो तो कौन सी विधि चुनें? — actor department_buyer→department_buyer; intent procurement_method_selection→procurement_planning; top5=True; final=True
- Q50 [Fail]: Tender me bid submit kaise karu? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q51 [Fail]: Submitted bid ko deadline se pehle modify aur resubmit kaise karein? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q62 [Fail]: How does the tender owner publish a completed tender? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q65 [Fail]: How does a tender owner issue an EMD/Bid Security Corrigendum? — actor department_operator→department_operator; intent corrigendum_portal_steps→emd_definition; top5=False; final=False
- Q66 [Partial]: How should the bid opener open the technical bid online? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q67 [Partial]: How does the department operator open the price bid? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q71 [Fail]: Department operator tender publish kaise kare? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q80 [Fail]: निविदा स्वामी निविदा प्रकाशित कैसे करे? — actor department_operator→department_operator; intent tender_publication_portal_steps→unknown; top5=False; final=False
- Q83 [Partial]: तकनीकी बोली खोलने की ऑनलाइन प्रक्रिया क्या है? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q91 [Fail]: What does open tender mean? — actor general_information_user→general_information_user; intent tender_method_definition→unknown; top5=False; final=False
- Q94 [Fail]: What do the Chhattisgarh Store Purchase Rules govern? — actor general_information_user→general_information_user; intent procurement_methods_overview→unknown; top5=True; final=True
- Q97 [Fail]: GeM aur state e-procurement portal me fark batao. — actor general_information_user→general_information_user; intent gem_eproc_comparison→gem_definition; top5=True; final=True
- Q99 [Fail]: Single tender kab allowed hota hai? — actor general_information_user→general_information_user; intent tender_method_definition→unknown; top5=True; final=False
- Q103 [Fail]: Store Purchase Rules CG kis purchase par apply hote hain? — actor general_information_user→general_information_user; intent procurement_methods_overview→unknown; top5=True; final=True
- Q104 [Partial]: छत्तीसगढ़ में सरकारी खरीद की अलग-अलग विधियाँ क्या हैं? — actor general_information_user→general_information_user; intent procurement_methods_overview→unknown; top5=True; final=True
- Q105 [Fail]: जेम क्या है? — actor general_information_user→general_information_user; intent gem_definition→unknown; top5=False; final=False
- Q106 [Fail]: जेम और छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल में क्या अंतर है? — actor general_information_user→general_information_user; intent gem_eproc_comparison→unknown; top5=True; final=False
- Q109 [Partial]: ईएमडी या बोली सुरक्षा का अर्थ क्या है? — actor general_information_user→general_information_user; intent emd_definition→unknown; top5=True; final=True
- Q116 [Fail]: Tender banana hai ya bid bharni hai, kya karu? — actor general_information_user→general_information_user; intent mixed_role_clarification→tender_creation_policy; top5=True; final=False
- Q120 [Fail]: निविदा बनानी है या बोली जमा करनी है? — actor general_information_user→general_information_user; intent mixed_role_clarification→unknown; top5=False; final=False

Likely files: 05_webui/fine_intent_policy.py; 05_webui/nlp_features.py

Minimal fix: Add or refine only the missing fine-intent route and its evidence contract.

Risk: Medium-high: overlapping keywords can reroute adjacent intents.

## context selection (7)

- Q40 [Fail]: How can I submit my technical and price bid online? — actor vendor_bidder→general_information_user; intent bid_submission_portal_steps→unknown; top5=True; final=False
- Q66 [Partial]: How should the bid opener open the technical bid online? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q67 [Partial]: How does the department operator open the price bid? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q83 [Partial]: तकनीकी बोली खोलने की ऑनलाइन प्रक्रिया क्या है? — actor department_operator→department_operator; intent bid_opening_portal_steps→unknown; top5=True; final=False
- Q99 [Fail]: Single tender kab allowed hota hai? — actor general_information_user→general_information_user; intent tender_method_definition→unknown; top5=True; final=False
- Q106 [Fail]: जेम और छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल में क्या अंतर है? — actor general_information_user→general_information_user; intent gem_eproc_comparison→unknown; top5=True; final=False
- Q116 [Fail]: Tender banana hai ya bid bharni hai, kya karu? — actor general_information_user→general_information_user; intent mixed_role_clarification→tender_creation_policy; top5=True; final=False

Likely files: 05_webui/app.py

Minimal fix: Preserve the already-retrieved authoritative family during adaptive context selection.

Risk: Medium: token-budget changes can alter latency and citations.

## language (4)

- Q51 [Fail]: Submitted bid ko deadline se pehle modify aur resubmit kaise karein? — actor vendor_bidder→vendor_bidder; intent bid_submission_portal_steps→unknown; top5=True; final=True
- Q78 [Fail]: Offline tendr portal pe upload kaise karna hai? — actor department_operator→general_information_user; intent tender_creation_portal_steps→unknown; top5=True; final=True
- Q94 [Fail]: What do the Chhattisgarh Store Purchase Rules govern? — actor general_information_user→general_information_user; intent procurement_methods_overview→unknown; top5=True; final=True
- Q99 [Fail]: Single tender kab allowed hota hai? — actor general_information_user→general_information_user; intent tender_method_definition→unknown; top5=True; final=False

Likely files: 05_webui/app.py; 05_webui/actor_boundary.py

Minimal fix: Preserve the query language directive and reject only the failing output-language pattern.

Risk: Medium.

## retrieval filtering (2)

- Q101 [Fail]: EMD kya hai aur kyu li jati hai? — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=False; final=False
- Q117 [Fail]: EMD ka process short me batao. — actor general_information_user→general_information_user; intent emd_definition→emd_definition; top5=False; final=False

Likely files: 05_webui/app.py; 04_embeddings_and_kg/scripts/embeddings_production.py

Minimal fix: Inspect expansion, metadata policy, hybrid scores and top-5 family filtering for the failing intent.

Risk: Medium: broad retrieval changes can regress passing intents.

## streaming (1)

- Q91 [Fail]: What does open tender mean? — actor general_information_user→general_information_user; intent tender_method_definition→unknown; top5=False; final=False

Likely files: 05_webui/app.py; 05_webui/streaming_utils.py; 05_webui/static/script.js

Minimal fix: Fix only the event lifecycle proven by the failing trace.

Risk: High: streaming is already verified and shared by all answers.

