from rest_framework import serializers
from proyecto_prevencion.models import OrganismoPublico, ComunaPlan, TiposMedidas, Medida, DocumentoRequerido, Indicador, DocumentoSubido, Usuario

class OrganismoPublicoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo OrganismoPublico.
    Proporciona una representación del organismo público, 
    incluyendo su nombre y estado de la actividad.

    Campos incluidos:
    - id: int
    - nombre_organismo: str
    - activo: bool
    """
    class Meta:
        model = OrganismoPublico
        fields = ['id', 'nombre_organismo', 'activo']

class ComunaPlanSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo ComunaPlan.
    Serializa la información de una comuna dentro del plan.

    Campos incluidos:
    - id: int
    - nombre_comuna: str
    - activo: bool
    """
    class Meta:
        model = ComunaPlan
        fields = ['id', 'nombre_comuna', 'activo']

class TiposMedidasSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo TiposMedidas.
    Convierte los tipos de medidas disponibles en un formato JSON para su uso en API.

    Campos incluidos:
    - id: int
    - nombre_tipo_medida: str
    - activo: bool
    """
    class Meta:
        model = TiposMedidas
        fields = ['id', 'nombre_tipo_medida', 'activo']

class DocumentoRequeridoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo DocumentoRequerido.
    Facilita la transferencia de información sobre documentos necesarios 
    asociados a una medida específica.

    Campos incluidos:
    - id: int
    - medida: int (clave foránea)
    - descripcion: str
    """
    class Meta:
        model = DocumentoRequerido
        fields = '__all__'

class MedidaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Medida.
    Proporciona una representación detallada de las medidas, 
    incluyendo datos asociados como el tipo, organismo público, 
    documentos requeridos, y atributos específicos como la fórmula y frecuencia.

    Incluye:
    - documentos_requeridos: lista de DocumentoRequeridoSerializer
    - tipo_medida: int (clave primaria de TiposMedidas)
    - organismo: int (clave primaria de OrganismoPublico)

    Campos incluidos:
    - id
    - tipo_medida
    - nombre_corto
    - nombre_largo
    - organismo
    - comunas
    - regulatorio
    - descripcion_formula
    - tipo_formula
    - frecuencia
    - proxima_fecha_carga
    - created_at
    - update_at
    - activo
    - documentos_requeridos
    """
    documentos_requeridos = DocumentoRequeridoSerializer(many=True, read_only=True)

    tipo_medida = serializers.PrimaryKeyRelatedField(
        queryset=TiposMedidas.objects.all(),
        help_text="ID del tipo de medida"
    )
    organismo = serializers.PrimaryKeyRelatedField(
        queryset=OrganismoPublico.objects.all(),
        help_text="ID del organismo asociado"
    )
    
    class Meta:
        model = Medida
        fields = [
            'id', 'tipo_medida', 'nombre_corto', 'nombre_largo', 'organismo',
            'comunas', 'regulatorio', 'descripcion_formula', 'tipo_formula',
            'frecuencia', 'proxima_fecha_carga', 'created_at', 'update_at',
            'activo', 'documentos_requeridos'
        ]

class IndicadorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Indicador.
    Serializa los datos relacionados con los indicadores, 
    como cálculo, estado de cumplimiento, y fechas clave.
    Permite integrar la información del indicador en los servicios de API.

    Campos incluidos:
    - id
    - medida
    - usuario
    - calculo_indicador
    - cumple_requisitos
    - fecha_reporte
    - fecha_aprobacion
    - fecha_rechazo
    - created_at
    - update_at
    - motivo_rechazo
    """
    class Meta:
        model = Indicador
        fields = [
            'id', 'medida', 'usuario', 'calculo_indicador',
            'cumple_requisitos', 'fecha_reporte', 'fecha_aprobacion',
            'fecha_rechazo', 'created_at', 'update_at', 'motivo_rechazo'
        ]

class DocumentoSubidoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo DocumentoSubido.
    Maneja la carga y representación de documentos asociados a indicadores,
    vinculando cada documento con el requerimiento y el indicador correspondiente.

    Campos incluidos:
    - id
    - indicador
    - documento_requerido
    - archivo
    """
    class Meta:
        model = DocumentoSubido
        fields = ['id', 'indicador', 'documento_requerido', 'archivo']

class RechazoIndicadorSerializer(serializers.Serializer):
    """
    Serializer utilizado para registrar el motivo del rechazo de un indicador.
    Contiene un único campo 'motivo', que detalla la razón específica del rechazo.

    Campos:
    - motivo: str, motivo del rechazo
    """
    motivo = serializers.CharField(help_text="Motivo del rechazo", required=True)

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario.
    Proporciona una representación completa de los usuarios del sistema, 
    incluyendo datos adicionales como el RUT, organismo asociado y su estado de aprobación.

    Campos incluidos:
    - id
    - username
    - email
    - first_name
    - last_name
    - rut_usuario
    - organismo
    - aprobado
    - is_superuser
    - is_staff
    - date_joined
    """
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rut_usuario', 'organismo', 'aprobado',
            'is_superuser', 'is_staff', 'date_joined'
        ]

class UsuarioRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer utilizado para registrar nuevos usuarios en el sistema.
    Gestiona campos básicos como nombre de usuario, correo, contraseña, 
    y otros atributos necesarios para la creación de la cuenta.

    Campos esperados:
    - username: str
    - email: str
    - password: str (solo escritura)
    - first_name: str
    - last_name: str
    - rut_usuario: str
    - organismo: int (clave foránea)

    El método create() encripta la contraseña y marca aprobado=False.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password',
            'first_name', 'last_name',
            'rut_usuario', 'organismo'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'help_text': 'Contraseña del usuario'},
            'email': {'help_text': 'Correo electrónico válido'}
        }

    def create(self, validated_data):
        """
        Crea y devuelve un nuevo Usuario con contraseña encriptada, create_user se encarga de esto.

        Parámetros
        ----------
        validated_data : dict
            Datos validados por el serializer.

        Retorna
        -------
        Usuario
            Instancia recién creada de Usuario.
        """
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            rut_usuario=validated_data.get('rut_usuario'),
            organismo=validated_data.get('organismo'),
            aprobado=False
        )
        return user
    
def generar_documentos_serializer(medida):
    """
    Genera dinámicamente un serializer para subir documentos basados en 
    los documentos requeridos por una medida específica. Esto permite 
    validar y procesar múltiples archivos según los requisitos de la medida.

    Parámetros
    ----------
    medida : Medida
        Instancia de Medida cuyos documentos requeridos se utilizarán.

    Retorna
    -------
    Serializer class
        Nueva clase Serializer con FileField por cada DocumentoRequerido.
    """
    campos = {}
    for doc in medida.documentos_requeridos.all():
        field_name = f'doc_{doc.id}'
        campos[field_name] = serializers.FileField(
            required=True,
            help_text=doc.descripcion,
            label=doc.descripcion
        )

    return type(
        f'DocumentoSubidoSerializerMedida{medida.id}',
        (serializers.Serializer,),
        campos
    )

class IndicadorEstadoSerializer(serializers.Serializer):
    """
    Serializer para representar el estado de un indicador. 
    Proporciona información detallada sobre la medida asociada y 
    atributos como cumplimiento de requisitos y fecha de reporte.

    Campos:
    - medida: MedidaSerializer
    - indicador_id: int (opcional)
    - cumple_requisitos: bool (opcional)
    - fecha_reporte: datetime (opcional)
    """
    medida = MedidaSerializer()
    indicador_id = serializers.IntegerField(required=False)
    cumple_requisitos = serializers.BooleanField(required=False)
    fecha_reporte = serializers.DateTimeField(required=False)

class DashboardDataSerializer(serializers.Serializer):
    """
    Serializer que organiza los datos para el dashboard. 
    Clasifica los indicadores en cuatro categorías principales: 
    aprobados, en revisión, rechazados, y pendientes de completar.

    Campos:
    - approved: lista de IndicadorEstadoSerializer
    - pending_review: lista de IndicadorEstadoSerializer
    - rejected: lista de IndicadorEstadoSerializer
    - pending_completion: lista de IndicadorEstadoSerializer
    """
    approved = IndicadorEstadoSerializer(many=True)
    pending_review = IndicadorEstadoSerializer(many=True)
    rejected = IndicadorEstadoSerializer(many=True)
    pending_completion = IndicadorEstadoSerializer(many=True)

class DashboardResponseSerializer(serializers.Serializer):
    """
    Serializer para estructurar la respuesta del dashboard. 
    Incluye un estado de éxito y un conjunto de datos organizados 
    en categorías utilizando el DashboardDataSerializer.

    Campos:
    - success: bool, indica si la operación fue exitosa
    - data: DashboardDataSerializer, indicadores agrupados
    """
    success = serializers.BooleanField()
    data = DashboardDataSerializer()