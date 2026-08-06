import logging
from celery import shared_task
from django_tenants.utils import schema_context
from django.conf import settings
from django.core.mail import send_mail
from apps.tenants.models import Client
from apps.orders.models.order import Order
from apps.orders.models.audit import OrderAuditLog

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def notify_order_created(self, tenant_schema_name, order_id):
    task_id = self.request.id
    retry_count = self.request.retries

    logger.info(
        f"[Celery Order Task] Initiating post-order creation notifications. "
        f"TaskID: {task_id} | Schema: {tenant_schema_name} | OrderID: {order_id} | Retry: {retry_count}"
    )

    try:
        tenant = Client.objects.get(schema_name=tenant_schema_name)
    except Client.DoesNotExist as err:
        logger.error(
            f"[Celery Order Task] Tenant schema '{tenant_schema_name}' not found. "
            f"TaskID: {task_id} | OrderID: {order_id} | Error: {str(err)}"
        )
        return "Tenant not found"

    with schema_context(tenant.schema_name):
        try:
            # 1. Fetch Order
            order = Order.objects.select_related("assigned_employee").get(id=order_id)
            
            # Idempotency check: verify if the notifications processed audit log already exists
            already_notified = OrderAuditLog.objects.filter(
                order=order,
                action="SYSTEM",
                changes__description="Post-order creation notifications processed."
            ).exists()

            if already_notified:
                logger.warning(
                    f"[Celery Order Task] Idempotency check triggered. Notifications already processed for Order {order.tracking_id}. "
                    f"TaskID: {task_id} | Schema: {tenant_schema_name} | OrderID: {order_id}"
                )
                return "Skipped: Notifications already processed"

            # 2. Customer Confirmation Email
            email_sent = False
            email_configured = bool(settings.EMAIL_HOST and settings.EMAIL_HOST_USER)
            
            if order.customer_email:
                if email_configured:
                    try:
                        subject = f"Order Confirmation - {order.tracking_id}"
                        message = f"""
Hello {order.customer_name},

Thank you for choosing TrackFlow AI. Your order has been registered successfully.

Tracking ID: {order.tracking_id}
Pickup From: {order.pickup_address}
Deliver To: {order.delivery_address}
Expected Delivery: {order.expected_delivery_date.strftime('%Y-%m-%d %H:%M') if order.expected_delivery_date else 'N/A'}
Priority: {order.priority}

You will be notified once the driver updates your delivery status.

Regards,

TrackFlow AI Team
"""
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[order.customer_email],
                            fail_silently=False,
                        )
                        email_sent = True
                        logger.info(f"[Celery Order Task] Confirmation email sent to customer {order.customer_email} for Order {order.tracking_id}.")
                    except Exception as email_err:
                        # Transport/networking failure triggers retry
                        raise email_err
                else:
                    logger.warning(
                        f"[Celery Order Task] EmailService is not configured. Skipping confirmation email for Order {order.tracking_id}. "
                        f"TaskID: {task_id} | Schema: {tenant_schema_name}"
                    )

            # 3. SMS Confirmation (Placeholder)
            logger.info(
                f"[Celery Order Task] SMS Integration unavailable. [Placeholder] Notification to customer phone: {order.customer_phone} skipped."
            )

            # 4. Notify Assigned Delivery Partner
            driver_notified = False
            if order.assigned_employee:
                driver = order.assigned_employee
                logger.info(
                    f"[Celery Order Task] [Placeholder] Delivery partner {driver.full_name} notified of assignment for Order {order.tracking_id}."
                )
                driver_notified = True

            # 5. In-App Notification (Placeholder)
            logger.info(
                f"[Celery Order Task] In-App Notification module unavailable. [Placeholder] In-app log created for customer {order.customer_name}."
            )

            # 6. Create OrderAuditLog
            OrderAuditLog.objects.create(
                order=order,
                action="SYSTEM",
                changed_by=None,
                changes={
                    "description": "Post-order creation notifications processed.",
                    "email_sent": email_sent,
                    "sms_sent": False,
                    "driver_notified": driver_notified,
                },
            )

            logger.info(
                f"[Celery Order Task] Post-order notifications completed successfully. "
                f"TaskID: {task_id} | Schema: {tenant_schema_name} | OrderID: {order_id}"
            )
            return "Notifications processed successfully"

        except Order.DoesNotExist as err:
            logger.error(
                f"[Celery Order Task] Order '{order_id}' not found in schema '{tenant_schema_name}'. "
                f"TaskID: {task_id} | Error: {str(err)}"
            )
            return "Order not found"

        except Exception as err:
            # Trigger task retry with exponential backoff on transport errors
            countdown = 60 * (2 ** retry_count)
            logger.warning(
                f"[Celery Order Task] Temporary failure processing notifications. Retrying task in {countdown}s. "
                f"TaskID: {task_id} | Schema: {tenant_schema_name} | OrderID: {order_id} | Error: {str(err)}"
            )
            try:
                self.retry(exc=err, countdown=countdown)
            except Exception as retry_err:
                logger.error(
                    f"[Celery Order Task] Max retries exceeded or queue error. "
                    f"TaskID: {task_id} | Schema: {tenant_schema_name} | OrderID: {order_id} | Error: {str(retry_err)}"
                )
                raise retry_err
