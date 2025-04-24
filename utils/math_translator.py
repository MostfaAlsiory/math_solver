import re
import logging

logger = logging.getLogger(__name__)

# قاموس ترجمة الرموز والمصطلحات الرياضية
MATH_TRANSLATION = {
    # رموز الدوال المثلثية
    r'sin\(': 'جا(',
    r'cos\(': 'جتا(',
    r'tan\(': 'ظا(',
    r'cot\(': 'ظتا(',
    r'sec\(': 'قا(',
    r'csc\(': 'قتا(',
    r'arcsin\(': 'قا⁻¹جا(',
    r'arccos\(': 'قا⁻¹جتا(',
    r'arctan\(': 'قا⁻¹ظا(',
    
    # المتغيرات الشائعة
    r'\bx\b': 'س',
    r'\by\b': 'ص',
    r'\bz\b': 'ع',
    r'\bt\b': 'ن',
    r'\ba\b': 'أ',
    r'\bb\b': 'ب',
    r'\bc\b': 'جـ',
    r'\br\b': 'نق',
    r'\bh\b': 'هـ',
    r'\bn\b': 'ن',
    r'\\bp\\b': 'ط',
    r'\bq\b': 'ث',
    r'\bk\b': 'ك',
    r'\bm\b': 'م',
    r'\bf\b': 'د',
    r'\bg\b': 'و',
    
    # رموز الدوال والعمليات الرياضية
    r'\bsin\b': 'جا',
    r'\bcos\b': 'جتا',
    r'\btan\b': 'ظا',
    r'\bcot\b': 'ظتا',
    r'\bsec\b': 'قا',
    r'\bcsc\b': 'قتا',
    r'\barcsin\b': 'قا⁻¹جا',
    r'\barccos\b': 'قا⁻¹جتا',
    r'\barctan\b': 'قا⁻¹ظا',
    r'\basin\b': 'قا⁻¹جا',
    r'\bacos\b': 'قا⁻¹جتا',
    r'\batan\b': 'قا⁻¹ظا',
    r'\blog\b': 'لو',
    r'\bln\b': 'لو',
    r'\bexp\b': 'أُس',
    r'\blim\b': 'نـها',
    r'\bmax\b': 'أقصى',
    r'\bmin\b': 'أدنى',
    r'\babs\b': 'مط',
    r'\barg\b': 'زا',
    r'\bsqrt\b': 'جذر',
    r'\bcbrt\b': '∛',
    
    # العمليات الحسابية
    r'\bplus\b': 'زائد',
    r'\bminus\b': 'ناقص',
    r'\btimes\b': 'ضرب',
    r'\bdivided by\b': 'مقسوم على',
    r'\bequals\b': 'يساوي',
    r'\bless than\b': 'أصغر من',
    r'\bgreater than\b': 'أكبر من',
    r'\bnot equal\b': 'لا يساوي',
    r'\bdivided by\b': 'مقسوم على',
    r'\bto the power of\b': 'أُس',
    
    # المصطلحات الرياضية
    r'\barea\b': 'المساحة',
    r'\bvolume\b': 'الحجم',
    r'\bcircle\b': 'دائرة',
    r'\bsphere\b': 'كرة',
    r'\btriangle\b': 'مثلث',
    r'\bsquare\b': 'مربع',
    r'\brectangle\b': 'مستطيل',
    r'\brhombus\b': 'معين',
    r'\btrapezoid\b': 'شبه منحرف',
    r'\bpolygon\b': 'مضلع',
    r'\bquadrilateral\b': 'رباعي الأضلاع',
    r'\binteger\b': 'عدد صحيح',
    r'\brational\b': 'عدد نسبي',
    r'\birrational\b': 'عدد غير نسبي',
    r'\breal\b': 'عدد حقيقي',
    r'\bcomplex\b': 'عدد مركب',
    r'\bimaginary\b': 'تخيلي',
    r'\bnatural\b': 'عدد طبيعي',
    r'\beven\b': 'زوجي',
    r'\bodd\b': 'فردي',
    r'\bprime\b': 'أولي',
    r'\bcomposite\b': 'مركب',
    r'\bdivisor\b': 'قاسم',
    r'\bfactor\b': 'عامل',
    r'\bmultiple\b': 'مضاعف',
    r'\bgcd\b': 'ق.م.أ',
    r'\blcm\b': 'م.م.أ',
    
    # التكامل والتفاضل
    r'\bintegral\b': 'تكامل',
    r'\bderivative\b': 'مشتقة',
    r'\bdifferential\b': 'تفاضل',
    r'\blimit\b': 'نهاية',
    r'\bfunction\b': 'دالة',
    r'\bcontinuous\b': 'متصلة',
    r'\bdifferentiable\b': 'قابلة للاشتقاق',
    r'\bintegrable\b': 'قابلة للتكامل',
    r'\bvector\b': 'متجه',
    r'\bmatrix\b': 'مصفوفة',
    r'\bdeterminant\b': 'محدد',
    r'\beigenvalue\b': 'قيمة ذاتية',
    r'\beigenvector\b': 'متجه ذاتي',
    r'\bpolynomial\b': 'كثيرة حدود',
    r'\bmonomial\b': 'أحادي الحد',
    r'\bbinomial\b': 'ثنائي الحد',
    r'\btrinomial\b': 'ثلاثي الحد',
    r'\bset\b': 'مجموعة',
    r'\bsubset\b': 'مجموعة جزئية',
    r'\bunion\b': 'اتحاد',
    r'\bintersection\b': 'تقاطع',
    r'\bcomplement\b': 'متممة',
    r'\bdifference\b': 'فرق',
    r'\bcartesian product\b': 'الجداء الديكارتي',
    
    # الإحصاء والاحتمالات
    r'\bsum\b': 'مجموع',
    r'\bproduct\b': 'جُداء',
    r'\broot\b': 'جذر',
    r'\bsquare root\b': 'الجذر التربيعي',
    r'\bcube root\b': 'الجذر التكعيبي',
    r'\bpower\b': 'أُس',
    r'\baverage\b': 'متوسط',
    r'\bmean\b': 'متوسط',
    r'\bmedian\b': 'وسيط',
    r'\bmode\b': 'منوال',
    r'\bvariance\b': 'تباين',
    r'\bstandard deviation\b': 'انحراف معياري',
    r'\bprobability\b': 'احتمال',
    r'\brandom\b': 'عشوائي',
    r'\bdistribution\b': 'توزيع',
    r'\bnormal distribution\b': 'التوزيع الطبيعي',
    r'\bbinomial distribution\b': 'توزيع ذي الحدين',
    r'\bexponential distribution\b': 'التوزيع الأسي',
    r'\bfrequency\b': 'تكرار',
    r'\bcorrelation\b': 'ارتباط',
    r'\bregression\b': 'انحدار',
    r'\bhypothesis\b': 'فرضية',
    r'\bsample\b': 'عينة',
    r'\bpopulation\b': 'مجتمع إحصائي',
    
    # تم إزالة أنماط تحويل الكسور من هنا لأنها تنفذ في وظيفة translate_math_text
    
    # رموز التكامل والتفاضل
    r'\\int': '∫',
    r'd/dx': 'د/دس',
    r'd/dy': 'د/دص',
    r'd/dz': 'د/دع',
    r'd/dt': 'د/دن',
    r'partial': '∂',
    r'nabla': '∇',
    r'delta': 'δ',
    r'epsilon': 'ε',
    r'theta': 'θ',
    r'alpha': 'α',
    r'beta': 'β',
    r'gamma': 'γ',
    r'pi': 'π',
    r'phi': 'φ',
    r'lambda': 'λ',
    r'mu': 'μ',
    r'sigma': 'σ',
    r'omega': 'ω',
    
    # بعض المصطلحات والرموز الإضافية
    r'diameter': 'قطر',
    r'circumference': 'محيط',
    r'perimeter': 'محيط',
    r'radius': 'نصف قطر',
    r'angle': 'زاوية',
    r'diagonal': 'قطر',
    r'height': 'ارتفاع',
    r'width': 'عرض',
    r'length': 'طول',
    r'constant': 'ثابت',
    r'variable': 'متغير',
    r'infinity': 'ما لا نهاية',
    r'infinity': '∞',
    r'equals': 'يساوي',
    r'equals': '=',
    r'theorem': 'نظرية',
    r'formula': 'صيغة',
    r'expression': 'تعبير',
    
    # أقسام ومحتويات Wolfram Alpha
    r'\bResult\b': 'النتيجة',
    r'\bPlot\b': 'الرسم البياني',
    r'\bGraph\b': 'الرسم البياني',
    r'\bAlternate form\b': 'صيغة بديلة',
    r'\bDefinition\b': 'التعريف',
    r'\bDefinite integral\b': 'التكامل المحدود',
    r'\bIndefinite integral\b': 'التكامل غير المحدود',
    r'\bDerivative\b': 'المشتقة',
    r'\bDerivatives\b': 'المشتقات',
    r'\bRoots\b': 'الجذور',
    r'\bSolutions\b': 'الحلول',
    r'\bSolution\b': 'الحل',
    r'\bSystem of equations\b': 'نظام معادلات',
    r'\bPartial derivative\b': 'المشتقة الجزئية',
    r'\bApproximation\b': 'التقريب',
    r'\bUnit conversion\b': 'تحويل الوحدات',
    r'\bDecimal form\b': 'الصيغة العشرية',
    r'\bGeometric figure\b': 'شكل هندسي',
    r'\bLimit\b': 'النهاية',
    r'\bSeries expansion\b': 'التوسعة المتسلسلة',
    r'\bExact result\b': 'النتيجة الدقيقة',
    r'\bProbability\b': 'الاحتمالية',
    r'\bStatistics\b': 'الإحصاء',
    r'\bEquation\b': 'المعادلة',
    r'\bProperties\b': 'الخصائص',
    r'\bPossible representations\b': 'التمثيلات الممكنة',
    r'\bFactorization\b': 'التحليل إلى عوامل',
    r'\bExpansion\b': 'البسط',
    r'\bNumber line\b': 'خط الأعداد',
    r'\bContinued fraction\b': 'الكسر المتصل',
    r'\bTruth table\b': 'جدول الحقيقة',
    r'\bAlternate forms\b': 'صيغ بديلة',
    r'\bAntiderivative\b': 'مضاد المشتقة',
    r'\bNumber theory\b': 'نظرية الأعداد',
    r'\bGeneral solution\b': 'الحل العام',
    r'\bParticular solution\b': 'الحل الخاص',
    r'\bLimits\b': 'النهايات',
    r'\bSeries\b': 'المتسلسلة',
    r'\bPlots\b': 'الرسوم البيانية',
    r'\bInput\b': 'المدخلات',
    r'\bInput interpretation\b': 'تفسير المدخلات',
    r'\bSymbolic solution\b': 'الحل الرمزي',
    r'\bHomogeneous solution\b': 'الحل المتجانس',
    r'\bNumerical solution\b': 'الحل العددي',
    r'\bAbsolute value\b': 'القيمة المطلقة',
    r'\bValue\b': 'القيمة',
    r'\bValues\b': 'القيم',
    r'\bIntegration\b': 'التكامل',
    r'\bDifferentiation\b': 'التفاضل',
    r'\bAlgebraic manipulation\b': 'المعالجة الجبرية',
    r'\bSimplification\b': 'التبسيط',
    r'\bExpanded form\b': 'الصيغة المبسوطة',
    r'\bFactored form\b': 'الصيغة المحللة',
    r'\bGraphical solution\b': 'الحل البياني',
    r'\bFormula\b': 'الصيغة',
    r'\bFurther information\b': 'معلومات إضافية',
    r'\bNumber properties\b': 'خصائص العدد',
    r'\bComputation\b': 'الحساب',
    r'\b3D plot\b': 'الرسم ثلاثي الأبعاد',
    r'\bContour plot\b': 'رسم الكنتور',
    r'\bVector plot\b': 'الرسم المتجهي',
    r'\bUse exact form\b': 'استخدام الصيغة الدقيقة',
    r'\bNumerical approximation\b': 'التقريب العددي',
    r'\bAlgebraic solution\b': 'الحل الجبري',
    r'\bTrigonometric form\b': 'الصيغة المثلثية',
    r'\bExponential form\b': 'الصيغة الأسية',
    r'\bLogarithmic form\b': 'الصيغة اللوغاريتمية',
    r'\bMixed number\b': 'العدد المختلط',
    r'\bTiming\b': 'التوقيت',
    r'\bRational approximation\b': 'التقريب النسبي',
    r'\bSignificant figures\b': 'الأرقام المعنوية',
    r'\bScientific notation\b': 'التدوين العلمي',
    r'\bEngineering notation\b': 'التدوين الهندسي',
    r'Step-by-step solution': 'الحل خطوة بخطوة',
    r'Input interpretation': 'تفسير المدخلات',
    r'Interpretation': 'التفسير',
    r'Visual representation': 'التمثيل البصري',
    r'Mathematical formula': 'الصيغة الرياضية',
    r'Differential equation': 'معادلة تفاضلية',
    r'Initial conditions': 'الشروط الأولية',
    r'Boundary conditions': 'شروط الحدود',
    r'Numerical solution': 'الحل العددي',
    r'Analytical solution': 'الحل التحليلي',
    r'General solution': 'الحل العام',
    r'Particular solution': 'الحل الخاص',
    r'Indefinite integral': 'التكامل غير المحدّد',
    r'Definite integral': 'التكامل المحدّد',
    r'Antiderivative': 'تكامل',
    r'Vector field': 'حقل متجهي',
    r'Scalar field': 'حقل عددي',
    r'Constraint': 'قيد',
    r'Domain': 'مجال',
    r'Range': 'مدى',
    r'Full simplification': 'التبسيط الكامل',
    r'Decimal approximation': 'التقريب العشري',
    r'Alternate forms': 'الصيغ البديلة',
    r'Physical quantities': 'الكميات الفيزيائية',
    r'Physical constants': 'الثوابت الفيزيائية',
    r'Physics formulas': 'صيغ فيزيائية',
    r'Chemistry formulas': 'صيغ كيميائية',
    r'Identities': 'متطابقات',
    r'Proof': 'برهان',
    r'Series': 'متسلسلة',
    r'Sequence': 'متتالية',
    r'Convergence': 'تقارب',
    r'Divergence': 'تباعد',
    r'Metric units': 'وحدات مترية',
    r'Imperial units': 'وحدات إمبراطورية',
    r'Conversion': 'تحويل',
    r'Result': 'النتيجة',
    r'Parametric plot': 'رسم بياني وسيطي',
    r'Polar plot': 'رسم بياني قطبي',
    r'Contour plot': 'رسم كنتوري',
    r'Surface plot': 'رسم سطحي',
    r'Vector plot': 'رسم متجهي',
    r'Directional field': 'حقل اتجاهي',
    
    # وحدات القياس
    r'meter': 'متر',
    r'gram': 'جرام',
    r'second': 'ثانية',
    r'ampere': 'أمبير',
    r'kelvin': 'كلفن',
    r'mole': 'مول',
    r'candela': 'شمعة',
    r'kilometer': 'كيلومتر',
    r'centimeter': 'سنتيمتر',
    r'millimeter': 'ملليمتر',
    r'kilogram': 'كيلوجرام',
    r'milligram': 'ملليجرام',
    r'hour': 'ساعة',
    r'minute': 'دقيقة',
    r'day': 'يوم',
    r'year': 'سنة',
    r'newton': 'نيوتن',
    r'joule': 'جول',
    r'watt': 'واط',
    r'volt': 'فولت',
    r'ohm': 'أوم',
    r'hertz': 'هرتز',
    r'pascal': 'باسكال',
    r'liter': 'لتر',
    r'milliliter': 'ملليلتر',
    r'inch': 'بوصة',
    r'foot': 'قدم',
    r'yard': 'ياردة',
    r'mile': 'ميل',
    r'pound': 'رطل',
    r'ounce': 'أونصة',
    r'gallon': 'جالون',
    r'fahrenheit': 'فهرنهايت',
    r'celsius': 'سيلسيوس',
    
    # مصطلحات فيزيائية
    r'velocity': 'سرعة',
    r'acceleration': 'تسارع',
    r'force': 'قوة',
    r'mass': 'كتلة',
    r'weight': 'وزن',
    r'density': 'كثافة',
    r'pressure': 'ضغط',
    r'energy': 'طاقة',
    r'power': 'قدرة',
    r'work': 'شغل',
    r'momentum': 'زخم',
    r'impulse': 'دفع',
    r'torque': 'عزم',
    r'friction': 'احتكاك',
    r'gravity': 'جاذبية',
    r'electric field': 'مجال كهربائي',
    r'magnetic field': 'مجال مغناطيسي',
    r'current': 'تيار',
    r'voltage': 'جهد',
    r'resistance': 'مقاومة',
    r'capacitance': 'سعة',
    r'inductance': 'حث',
    r'frequency': 'تردد',
    r'wavelength': 'طول موجي',
    r'amplitude': 'سعة',
    r'period': 'دور',
    r'temperature': 'درجة حرارة',
    r'heat': 'حرارة',
    r'entropy': 'إنتروبيا',
    r'efficiency': 'كفاءة'
}

def translate_math_text(text):
    """
    تحويل النص الرياضي من الإنجليزية إلى العربية
    
    Args:
        text (str): النص الرياضي بالإنجليزية
        
    Returns:
        str: النص الرياضي بعد التحويل إلى العربية
    """
    if not text:
        return text
    
    try:
        # استبدال كل الرموز والمصطلحات الموجودة في القاموس
        translated = text
        
        # أولاً: تحويل الكسور قبل أي تعديلات أخرى
        # البحث عن الكسور بتنسيق رقم/رقم أو رمز/رقم أو رقم/رمز
        translated = re.sub(r'(\d+)/(\d+)', r'$\\frac{\1}{\2}$', translated)
        translated = re.sub(r'([a-zA-Z])/(\d+)', r'$\\frac{\1}{\2}$', translated)
        translated = re.sub(r'(\d+)/([a-zA-Z])', r'$\\frac{\1}{\2}$', translated)
        translated = re.sub(r'([a-zA-Z])/([a-zA-Z])', r'$\\frac{\1}{\2}$', translated)
        
        # ثم تطبيق باقي الترجمات
        for eng_pattern, ar_replacement in MATH_TRANSLATION.items():
            # تخطي أنماط تحويل الكسور لأننا قمنا بها بالفعل
            if r'/(' in eng_pattern:
                continue
            translated = re.sub(eng_pattern, ar_replacement, translated)
        
        # تحويل الرموز المتغيرة في تعبيرات الكسور
        translated = re.sub(r'\\frac{x}', r'\\frac{س}', translated)
        translated = re.sub(r'\\frac{y}', r'\\frac{ص}', translated)
        translated = re.sub(r'\\frac{z}', r'\\frac{ع}', translated)
        translated = re.sub(r'\\frac{t}', r'\\frac{ن}', translated)
        translated = re.sub(r'}{x}', r'}{س}', translated)
        translated = re.sub(r'}{y}', r'}{ص}', translated)
        translated = re.sub(r'}{z}', r'}{ع}', translated)
        translated = re.sub(r'}{t}', r'}{ن}', translated)
        
        # تحويل الأسس من شكل x^2 إلى س²
        translated = re.sub(r'x\^2', 'س²', translated)
        translated = re.sub(r'x\^3', 'س³', translated)
        translated = re.sub(r'y\^2', 'ص²', translated)
        translated = re.sub(r'y\^3', 'ص³', translated)
        translated = re.sub(r'z\^2', 'ع²', translated)
        translated = re.sub(r'z\^3', 'ع³', translated)
        
        # تحويل الأسس من شكل a^n إلى شكل أفضل
        translated = re.sub(r'([a-zA-Zأ-ي])\^(\d+)', r'\1<sup>\2</sup>', translated)
        
        # تحويل العلامات الرياضية الإنجليزية إلى عربية
        translated = translated.replace(' + ', ' + ')
        translated = translated.replace(' - ', ' - ')
        translated = translated.replace(' * ', ' × ')
        translated = translated.replace(' / ', ' ÷ ')
        
        return translated
    except Exception as e:
        logger.error(f"خطأ أثناء ترجمة النص الرياضي: {e}")
        return text  # في حالة حدوث خطأ، إرجاع النص الأصلي

def translate_math_pods(pods_data):
    """
    تحويل محتوى الـpods الرياضية من Wolfram Alpha
    
    Args:
        pods_data (list): قائمة من pods مع البيانات النصية والصور
        
    Returns:
        list: قائمة محدثة بعد ترجمة النصوص
    """
    if not pods_data:
        return pods_data
    
    try:
        for pod in pods_data:
            # ترجمة عنوان الـpod
            pod['title'] = translate_math_text(pod['title'])
            
            # ترجمة محتوى النص في كل subpod
            for subpod in pod.get('subpods', []):
                if 'text' in subpod and subpod['text']:
                    subpod['text'] = translate_math_text(subpod['text'])
        
        return pods_data
    except Exception as e:
        logger.error(f"خطأ أثناء ترجمة pods الرياضية: {e}")
        return pods_data  # في حالة حدوث خطأ، إرجاع البيانات الأصلية