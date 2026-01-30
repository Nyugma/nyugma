"""
Generate sample legal document dataset for testing.

This script creates 10-20 sample legal documents with realistic content,
generates corresponding metadata, and pre-computes TF-IDF vectors.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

from src.components.case_repository import CaseRepository
from src.components.legal_vectorizer import LegalVectorizer
from src.components.text_preprocessor import TextPreprocessor
from src.components.pdf_processor import PDFProcessor
from src.models.case_document import CaseDocument
from src.models.legal_vocabulary import LegalVocabulary


# Sample legal case templates
CASE_TEMPLATES = [
    {
        "title": "Smith v. Johnson Family Custody Dispute",
        "category": "family_law",
        "content": """
        This matter comes before the court regarding the custody arrangement of minor children
        following the dissolution of marriage between petitioner Sarah Smith and respondent
        Michael Johnson. The parties were married on June 15, 2010, and have two minor children,
        ages 8 and 5. The petitioner seeks primary physical custody with joint legal custody.
        
        The court has considered the best interests of the children, including their relationship
        with each parent, the stability of each home environment, and the children's educational
        and emotional needs. Evidence presented includes testimony from both parents, a custody
        evaluation report, and statements from the children's teachers and counselors.
        
        After careful consideration of all evidence and applicable law, the court finds that
        joint legal custody with primary physical custody to the petitioner serves the best
        interests of the minor children. The respondent shall have parenting time every other
        weekend and one evening per week. Both parties shall participate in co-parenting
        counseling to facilitate effective communication regarding the children's welfare.
        
        Child support shall be calculated according to state guidelines based on the parties'
        respective incomes. The respondent shall maintain health insurance for the minor children
        and both parties shall share unreimbursed medical expenses equally.
        """
    },
    {
        "title": "Anderson Property Boundary Dispute",
        "category": "property_law",
        "content": """
        This action concerns a boundary dispute between neighboring property owners, plaintiff
        Robert Anderson and defendant Patricia Williams. The properties in question are located
        at 123 Oak Street and 125 Oak Street, respectively. The dispute arose when the defendant
        erected a fence that the plaintiff alleges encroaches upon his property by approximately
        three feet along a 50-foot boundary line.
        
        The plaintiff presented a recent survey conducted by a licensed surveyor showing the
        legal boundary line and demonstrating the encroachment. The defendant countered with
        evidence of adverse possession, claiming continuous and open use of the disputed area
        for over 20 years, including maintenance of landscaping and a garden shed.
        
        The court finds that while the defendant has used the disputed area, the use does not
        meet all requirements for adverse possession under state law. Specifically, the use was
        not hostile or adverse to the plaintiff's interests, as there was no clear demarcation
        or assertion of ownership until the recent fence installation.
        
        Therefore, the court orders the defendant to remove the fence and restore the boundary
        to its legal location as established by the survey. The defendant shall bear all costs
        associated with the fence removal and boundary restoration. The plaintiff is awarded
        reasonable attorney fees and court costs.
        """
    },
    {
        "title": "Martinez Employment Discrimination Case",
        "category": "employment_law",
        "content": """
        Plaintiff Maria Martinez brings this action against defendant TechCorp Industries
        alleging employment discrimination based on gender and national origin in violation
        of Title VII of the Civil Rights Act. The plaintiff was employed as a software engineer
        from January 2018 until her termination in March 2022.
        
        The plaintiff alleges she was subjected to a hostile work environment, including
        derogatory comments about her gender and ethnicity, exclusion from important meetings
        and projects, and ultimately wrongful termination in retaliation for complaints to
        human resources. The plaintiff seeks reinstatement, back pay, compensatory damages,
        and punitive damages.
        
        The defendant denies all allegations and asserts the plaintiff was terminated for
        legitimate, non-discriminatory reasons related to performance issues and violation
        of company policies. The defendant presented performance reviews and documentation
        of policy violations.
        
        After reviewing all evidence, including testimony from multiple witnesses and
        documentary evidence, the court finds that the plaintiff has established a prima facie
        case of discrimination and retaliation. The defendant's proffered reasons for
        termination are found to be pretextual. The court awards the plaintiff back pay,
        compensatory damages for emotional distress, and attorney fees. Reinstatement is
        not ordered due to the hostile nature of the relationship between the parties.
        """
    },
    {
        "title": "Thompson Contract Breach - Construction Dispute",
        "category": "contract_law",
        "content": """
        This matter involves a breach of contract claim brought by plaintiff David Thompson
        against defendant BuildRight Construction Company. The parties entered into a written
        contract on May 1, 2021, for the construction of a residential addition with a contract
        price of $150,000 and completion date of December 1, 2021.
        
        The plaintiff alleges the defendant failed to complete the work by the agreed deadline,
        performed substandard work requiring costly repairs, and abandoned the project before
        completion. The plaintiff seeks damages for breach of contract, including the cost to
        complete the work, repair defective work, and consequential damages for delay.
        
        The defendant counterclaims for unpaid contract balance, asserting the plaintiff failed
        to make progress payments as required and made unreasonable demands for changes beyond
        the scope of the original contract. The defendant seeks payment of the remaining
        contract balance plus additional compensation for extra work performed.
        
        The court finds both parties partially at fault. The defendant did breach the contract
        by failing to meet the completion deadline and performing certain work below industry
        standards. However, the plaintiff also breached by withholding payments without proper
        justification. The court awards the plaintiff damages for defective work and delay,
        offset by the unpaid contract balance owed to the defendant. Each party shall bear
        their own attorney fees.
        """
    },
    {
        "title": "Wilson Estate Probate Proceedings",
        "category": "probate_law",
        "content": """
        This matter concerns the probate of the estate of deceased testator Harold Wilson,
        who passed away on January 15, 2023. The decedent left a will dated March 10, 2020,
        naming his daughter Jennifer Wilson as executor and primary beneficiary. The decedent's
        son, Robert Wilson, contests the will, alleging undue influence and lack of testamentary
        capacity.
        
        The contestant alleges that at the time of will execution, the decedent was suffering
        from dementia and was unduly influenced by his daughter, who had power of attorney
        and controlled access to the decedent. The contestant seeks to invalidate the will
        and distribute the estate according to intestacy laws.
        
        The proponent of the will presented testimony from the attorney who drafted the will,
        the decedent's physician, and other witnesses attesting to the decedent's mental
        capacity and independent decision-making. Medical records show the decedent was
        competent at the time of will execution.
        
        After careful review of all evidence and testimony, the court finds the contestant
        has failed to meet the burden of proof to invalidate the will. The evidence supports
        that the decedent had testamentary capacity and was not subject to undue influence.
        The will is admitted to probate and the named executor is authorized to administer
        the estate according to its terms.
        """
    },
    {
        "title": "Green Environmental Compliance Violation",
        "category": "environmental_law",
        "content": """
        The Environmental Protection Agency brings this enforcement action against defendant
        GreenTech Manufacturing for violations of the Clean Water Act. The defendant operates
        a chemical manufacturing facility that discharges wastewater into the municipal
        treatment system under a permit issued pursuant to the National Pollutant Discharge
        Elimination System.
        
        The EPA alleges the defendant exceeded permitted discharge limits for heavy metals
        and toxic chemicals on multiple occasions between January 2021 and June 2022. The
        violations were discovered through routine monitoring and inspection. The EPA seeks
        civil penalties, injunctive relief requiring compliance, and implementation of
        enhanced monitoring and treatment systems.
        
        The defendant acknowledges the violations but asserts they were due to equipment
        malfunction and were promptly corrected upon discovery. The defendant has since
        invested in upgraded treatment equipment and enhanced monitoring systems. The
        defendant requests reduced penalties based on good faith efforts to achieve compliance.
        
        The court finds the defendant liable for the violations but recognizes the defendant's
        cooperation and remedial measures. The court imposes civil penalties of $250,000,
        requires continued compliance monitoring for three years, and orders implementation
        of the enhanced treatment systems. The defendant shall submit quarterly compliance
        reports to the EPA.
        """
    },
    {
        "title": "Davis Personal Injury - Automobile Accident",
        "category": "tort_law",
        "content": """
        Plaintiff Susan Davis brings this personal injury action against defendant James Brown
        arising from an automobile accident that occurred on Highway 101 on September 15, 2022.
        The plaintiff alleges the defendant was negligent in operating his vehicle, causing
        a rear-end collision that resulted in serious injuries to the plaintiff.
        
        The plaintiff sustained injuries including whiplash, herniated disc, and traumatic
        brain injury requiring extensive medical treatment and ongoing therapy. The plaintiff
        seeks damages for medical expenses, lost wages, pain and suffering, and loss of
        enjoyment of life. Total claimed damages exceed $500,000.
        
        The defendant admits liability for the accident but disputes the extent and causation
        of the plaintiff's injuries. The defendant's expert witnesses testified that some of
        the plaintiff's claimed injuries were pre-existing or unrelated to the accident. The
        defendant argues the claimed damages are excessive and not supported by the evidence.
        
        After trial, the jury found the defendant negligent and awarded the plaintiff $350,000
        in damages, including $150,000 for medical expenses, $50,000 for lost wages, and
        $150,000 for pain and suffering. The court enters judgment in favor of the plaintiff
        in the amount of $350,000 plus pre-judgment interest and costs.
        """
    },
    {
        "title": "Roberts Intellectual Property - Patent Infringement",
        "category": "intellectual_property",
        "content": """
        Plaintiff InnovateTech Corporation brings this patent infringement action against
        defendant TechSolutions Inc., alleging infringement of U.S. Patent No. 10,123,456
        entitled "Method and System for Data Processing." The patent covers a novel algorithm
        for processing large datasets efficiently.
        
        The plaintiff alleges the defendant's product, DataPro 5.0, incorporates the patented
        technology without authorization. The plaintiff seeks injunctive relief, damages for
        past infringement, and enhanced damages for willful infringement. The plaintiff
        presented evidence of the defendant's knowledge of the patent and deliberate copying.
        
        The defendant denies infringement and asserts the patent is invalid due to prior art
        and lack of non-obviousness. The defendant presented evidence of similar algorithms
        published before the patent filing date. Alternatively, the defendant argues its
        product does not practice all elements of the claimed invention.
        
        After claim construction and review of expert testimony, the court finds the patent
        valid and infringed by the defendant's product. However, the court finds the
        infringement was not willful, as the defendant had a reasonable basis to believe
        the patent was invalid. The court awards the plaintiff damages based on a reasonable
        royalty and enjoins the defendant from further infringement. Enhanced damages are
        denied.
        """
    },
    {
        "title": "Miller Criminal Appeal - Drug Possession",
        "category": "criminal_law",
        "content": """
        Defendant John Miller appeals his conviction for possession of controlled substances
        with intent to distribute. The defendant was convicted after a jury trial and sentenced
        to five years imprisonment. On appeal, the defendant raises three issues: sufficiency
        of evidence, improper admission of evidence, and ineffective assistance of counsel.
        
        The defendant argues the evidence was insufficient to prove intent to distribute, as
        the quantity of drugs found was consistent with personal use. The defendant also
        challenges the admission of evidence obtained during a warrantless search, arguing
        the search violated his Fourth Amendment rights.
        
        The State responds that the evidence was sufficient, including the quantity of drugs,
        packaging materials, scales, and large amounts of cash found in the defendant's
        possession. The State argues the search was lawful as incident to a valid arrest
        based on probable cause.
        
        After reviewing the record, this court finds the evidence sufficient to support the
        conviction. The warrantless search was justified as incident to arrest. However, the
        court finds merit in the ineffective assistance of counsel claim, as trial counsel
        failed to object to prejudicial testimony and did not present available exculpatory
        evidence. The conviction is reversed and the case is remanded for a new trial.
        """
    },
    {
        "title": "Chen Immigration Asylum Application",
        "category": "immigration_law",
        "content": """
        Petitioner Li Chen seeks review of the Board of Immigration Appeals' denial of her
        application for asylum. The petitioner, a citizen of China, entered the United States
        in 2020 and applied for asylum based on persecution due to her political opinions
        and membership in a particular social group.
        
        The petitioner testified that she was detained and tortured by Chinese authorities
        for participating in pro-democracy activities and that she fears persecution if
        returned to China. The petitioner presented evidence of her political activities,
        medical records documenting injuries, and country condition reports on human rights
        violations in China.
        
        The immigration judge denied the application, finding the petitioner's testimony not
        credible due to inconsistencies and lack of corroborating evidence. The Board of
        Immigration Appeals affirmed the denial. The petitioner argues the credibility
        determination was not supported by substantial evidence and the judge failed to
        consider all relevant evidence.
        
        This court finds the immigration judge's credibility determination was not supported
        by substantial evidence. The alleged inconsistencies were minor and adequately
        explained. The judge failed to properly consider corroborating evidence and country
        condition reports. The case is remanded to the Board of Immigration Appeals for
        further proceedings consistent with this opinion.
        """
    },
    {
        "title": "Baker Corporate Merger Antitrust Review",
        "category": "antitrust_law",
        "content": """
        The Federal Trade Commission challenges the proposed merger between MegaCorp Inc.
        and TechGiant Corporation, alleging the merger would substantially lessen competition
        in the software services market in violation of Section 7 of the Clayton Act. The
        FTC seeks a preliminary injunction to prevent the merger pending administrative
        proceedings.
        
        The FTC alleges the merged entity would control over 60% of the relevant market,
        creating a dominant position that would harm competition and consumers. The FTC
        presented economic analysis showing likely price increases and reduced innovation
        following the merger. The FTC argues the merger would eliminate head-to-head
        competition between the two largest competitors in the market.
        
        The merging parties argue the relevant market is defined too narrowly and that
        numerous competitors would remain post-merger. The parties presented evidence of
        low barriers to entry, rapid technological change, and strong competition from
        international firms. The parties argue the merger would create efficiencies
        benefiting consumers.
        
        After considering all evidence and testimony, the court finds the FTC has demonstrated
        a likelihood of success on the merits. The proposed merger would likely substantially
        lessen competition in the relevant market. The claimed efficiencies are insufficient
        to outweigh the anticompetitive effects. The court grants the preliminary injunction
        preventing the merger pending the outcome of administrative proceedings.
        """
    },
    {
        "title": "Foster Medical Malpractice Claim",
        "category": "medical_malpractice",
        "content": """
        Plaintiff Elizabeth Foster brings this medical malpractice action against defendant
        Dr. Richard Stevens and City Hospital arising from surgical complications. The
        plaintiff underwent gallbladder removal surgery performed by the defendant on
        March 20, 2022. During the surgery, the defendant allegedly severed the plaintiff's
        bile duct, requiring additional emergency surgery and prolonged hospitalization.
        
        The plaintiff alleges the defendant was negligent in performing the surgery and
        failed to meet the applicable standard of care. The plaintiff's expert witness, a
        board-certified surgeon, testified the bile duct injury was caused by the defendant's
        failure to properly identify anatomical structures and use appropriate surgical
        technique. The plaintiff seeks damages for additional medical expenses, pain and
        suffering, and permanent injury.
        
        The defendant denies negligence and asserts the bile duct injury was a known risk
        of the surgery that can occur even with proper technique. The defendant's expert
        testified the surgery was performed according to accepted standards and the injury
        was an unavoidable complication. The defendant argues the plaintiff was properly
        informed of the risks through the consent process.
        
        The jury found the defendant negligent and awarded the plaintiff $750,000 in damages.
        The court finds the verdict supported by the evidence and enters judgment accordingly.
        The defendant's motion for judgment notwithstanding the verdict is denied.
        """
    },
    {
        "title": "Nelson Bankruptcy Chapter 11 Reorganization",
        "category": "bankruptcy_law",
        "content": """
        Debtor Nelson Manufacturing Company filed a voluntary petition for relief under
        Chapter 11 of the Bankruptcy Code. The debtor operates a manufacturing business
        with 200 employees and seeks to reorganize its debts while continuing operations.
        The debtor has filed a plan of reorganization and disclosure statement.
        
        The proposed plan provides for payment of secured creditors in full over five years,
        payment of priority claims in full, and payment of unsecured creditors at 40 cents
        on the dollar over three years. The plan proposes to reject certain unprofitable
        contracts and leases. The debtor argues the plan is feasible based on projected
        future earnings and cost reductions.
        
        The Official Committee of Unsecured Creditors objects to the plan, arguing the
        proposed payment to unsecured creditors is inadequate and the plan is not feasible.
        The committee presented evidence that the debtor's financial projections are overly
        optimistic and the proposed cost reductions are unrealistic.
        
        After hearing, the court finds the plan meets the requirements of the Bankruptcy
        Code. The plan is fair and equitable, provides adequate protection to creditors,
        and is feasible. The disclosure statement is approved and the court sets a date
        for the confirmation hearing. Creditors shall have 30 days to vote on the plan.
        """
    },
    {
        "title": "Parker Securities Fraud Class Action",
        "category": "securities_law",
        "content": """
        This securities fraud class action is brought on behalf of all persons who purchased
        common stock of TechStart Inc. between January 1, 2021 and December 31, 2021. The
        plaintiffs allege the defendants made materially false and misleading statements
        regarding the company's financial condition and business prospects in violation of
        Section 10(b) of the Securities Exchange Act and Rule 10b-5.
        
        The plaintiffs allege the defendants knew or recklessly disregarded that the company's
        revenue recognition practices were improper and that reported revenues were materially
        overstated. When the truth was revealed, the stock price declined by 60%, causing
        substantial losses to investors. The plaintiffs seek damages, attorney fees, and costs.
        
        The defendants move to dismiss the complaint, arguing the plaintiffs have failed to
        plead fraud with the particularity required by Rule 9(b) and have not adequately
        alleged scienter. The defendants argue the challenged statements were forward-looking
        statements protected by the safe harbor provision.
        
        The court denies the motion to dismiss. The complaint adequately pleads specific
        false statements, their falsity, and facts giving rise to a strong inference of
        scienter. The safe harbor does not apply because the statements were not accompanied
        by meaningful cautionary language. The case shall proceed to discovery.
        """
    },
    {
        "title": "Hughes Tax Court Appeal - Business Deductions",
        "category": "tax_law",
        "content": """
        Petitioner James Hughes challenges the Internal Revenue Service's disallowance of
        business expense deductions claimed on his 2020 federal income tax return. The
        petitioner, a self-employed consultant, claimed deductions totaling $85,000 for
        home office expenses, travel, meals, and entertainment.
        
        The IRS disallowed $60,000 of the claimed deductions, asserting the expenses were
        personal in nature or not adequately substantiated. The IRS issued a notice of
        deficiency assessing additional tax, interest, and penalties. The petitioner timely
        filed a petition in Tax Court challenging the deficiency.
        
        The petitioner presented evidence including receipts, credit card statements, and
        testimony regarding the business purpose of the expenses. The petitioner argues all
        expenses were ordinary and necessary business expenses properly deductible under
        Section 162 of the Internal Revenue Code.
        
        The court finds the petitioner has substantiated $40,000 of the disputed deductions
        but failed to adequately substantiate the remaining $20,000. The home office
        deduction is allowed as the space was used exclusively and regularly for business.
        However, certain travel and entertainment expenses were personal or lacked adequate
        documentation. The deficiency is reduced accordingly and penalties are abated due
        to reasonable cause.
        """
    },
    {
        "title": "Coleman Education Law - Special Education Services",
        "category": "education_law",
        "content": """
        Plaintiffs, parents of student Emma Coleman, bring this action against the City
        School District under the Individuals with Disabilities Education Act (IDEA) and
        Section 504 of the Rehabilitation Act. The plaintiffs allege the district failed
        to provide their daughter with a free appropriate public education (FAPE) and seek
        compensatory education services and reimbursement for private school tuition.
        
        The student has been diagnosed with autism spectrum disorder and requires specialized
        instruction and related services. The plaintiffs allege the district's Individualized
        Education Program (IEP) was inadequate and the district failed to implement the
        services specified in the IEP. The plaintiffs unilaterally placed the student in
        a private special education school and seek reimbursement.
        
        The district argues the IEP was reasonably calculated to enable the student to make
        progress and the district offered FAPE. The district presented evidence of the
        student's progress under the IEP and the qualifications of the staff providing
        services. The district argues the private placement was unnecessary and inappropriate.
        
        After reviewing the administrative record and hearing testimony, the court finds
        the district failed to provide FAPE. The IEP goals were not appropriate for the
        student's needs and the district failed to implement key services. The private
        placement was appropriate. The court orders the district to reimburse the plaintiffs
        for private school tuition and provide compensatory education services.
        """
    }
]


def create_pdf_document(title: str, content: str, output_path: Path) -> None:
    """Create a PDF document with the given title and content."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify',
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='CaseTitle',
        alignment=TA_CENTER,
        fontSize=16,
        leading=20,
        spaceAfter=30,
        fontName='Helvetica-Bold'
    ))
    
    # Add title
    title_para = Paragraph(title, styles['CaseTitle'])
    elements.append(title_para)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Add content paragraphs
    paragraphs = content.strip().split('\n\n')
    for para_text in paragraphs:
        if para_text.strip():
            para = Paragraph(para_text.strip(), styles['Justify'])
            elements.append(para)
            elements.append(Spacer(1, 0.1 * inch))
    
    # Build PDF
    doc.build(elements)


def generate_sample_dataset(num_cases: int = 15) -> None:
    """
    Generate sample legal document dataset.
    
    Args:
        num_cases: Number of sample cases to generate (default: 15)
    """
    print(f"Generating {num_cases} sample legal documents...")
    
    # Initialize components
    repo = CaseRepository()
    pdf_processor = PDFProcessor()
    text_preprocessor = TextPreprocessor()
    vocabulary = LegalVocabulary()
    vectorizer = LegalVectorizer(vocabulary)
    
    # Create cases directory if it doesn't exist
    cases_dir = Path("data/cases")
    cases_dir.mkdir(parents=True, exist_ok=True)
    
    # Select cases to generate (with repetition if needed)
    selected_templates = []
    for i in range(num_cases):
        template = CASE_TEMPLATES[i % len(CASE_TEMPLATES)].copy()
        selected_templates.append(template)
    
    # Generate PDF files
    print("\nCreating PDF files...")
    case_documents = []
    all_texts = []
    
    for i, template in enumerate(selected_templates):
        case_id = f"case_{i+1:03d}"
        file_name = f"{case_id}.pdf"
        file_path = cases_dir / file_name
        
        # Create PDF
        create_pdf_document(template["title"], template["content"], file_path)
        print(f"  Created: {file_name}")
        
        # Extract text from PDF
        text = pdf_processor.extract_text(str(file_path))
        
        # Preprocess text
        processed_text = text_preprocessor.preprocess(text)
        all_texts.append(processed_text)
        
        # Generate random date within last 5 years
        days_ago = random.randint(0, 1825)  # 5 years
        case_date = datetime.now() - timedelta(days=days_ago)
        
        # Create case document
        case_doc = CaseDocument(
            case_id=case_id,
            title=template["title"],
            date=case_date,
            file_path=f"data/cases/{file_name}",
            text_content=processed_text,
            metadata={
                "category": template["category"],
                "word_count": len(processed_text.split()),
                "generated": True
            }
        )
        case_documents.append(case_doc)
    
    # Fit vectorizer on all documents
    print("\nTraining TF-IDF vectorizer...")
    vectorizer.fit(all_texts)
    
    # Save vectorizer model
    model_path = Path("data/vectorizer_model.pkl")
    vectorizer.save_model(model_path)
    print(f"  Saved vectorizer model to: {model_path}")
    
    # Generate vectors for all documents
    print("\nGenerating TF-IDF vectors...")
    vectors = vectorizer.transform(all_texts)
    
    # Save cases to repository
    print("\nSaving cases to repository...")
    for i, (case_doc, vector) in enumerate(zip(case_documents, vectors)):
        repo.add_case(case_doc, vector)
        print(f"  Added case {i+1}/{num_cases}: {case_doc.case_id}")
    
    # Validate repository
    print("\nValidating repository...")
    validation_results = repo.validate_repository()
    
    if validation_results['consistent']:
        print("  ✓ Repository validation passed")
        print(f"  ✓ Total cases: {validation_results['metadata_count']}")
        print(f"  ✓ Total vectors: {validation_results['vector_count']}")
    else:
        print("  ✗ Repository validation failed:")
        for issue in validation_results['issues']:
            print(f"    - {issue}")
    
    print("\n" + "="*60)
    print("Sample dataset generation complete!")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - {num_cases} PDF documents in data/cases/")
    print(f"  - Metadata file: data/cases_metadata.json")
    print(f"  - Vector file: data/vectors/case_vectors.pkl")
    print(f"  - Vectorizer model: data/vectorizer_model.pkl")
    print(f"\nYou can now test the application with these sample documents.")


if __name__ == "__main__":
    # Generate 15 sample cases by default
    num_cases = 15
    if len(sys.argv) > 1:
        try:
            num_cases = int(sys.argv[1])
            if num_cases < 1 or num_cases > 20:
                print("Number of cases must be between 1 and 20")
                sys.exit(1)
        except ValueError:
            print("Invalid number of cases")
            sys.exit(1)
    
    generate_sample_dataset(num_cases)
