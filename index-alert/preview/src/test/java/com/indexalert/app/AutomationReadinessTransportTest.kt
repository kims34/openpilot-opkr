package com.indexalert.app

import org.junit.Assert.*
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.IOException
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL

class AutomationReadinessTransportTest {
    private class Connection(
        private val status: Int = HTTP_OK,
        val body: InputStream = ByteArrayInputStream("{}".toByteArray()),
        private val statusFailure: Boolean = false
    ) : HttpURLConnection(URL("https://example.invalid/automation/readiness")) {
        var disconnected = false
        var bodyRequested = false
        override fun connect() = Unit
        override fun usingProxy() = false
        override fun disconnect() { disconnected = true }
        override fun getResponseCode(): Int {
            if (statusFailure) throw IOException("status unavailable")
            return status
        }
        override fun getInputStream(): InputStream {
            bodyRequested = true
            return body
        }
    }

    @Test fun successfulGetUsesFixedTimeoutsAndNeverFollowsRedirects() {
        val connection = Connection()
        connection.instanceFollowRedirects = true
        assertEquals("{}", AutomationReadiness.fetchReadinessText(connection))
        assertEquals("GET", connection.requestMethod)
        assertFalse(connection.instanceFollowRedirects)
        assertEquals(5000, connection.connectTimeout)
        assertEquals(5000, connection.readTimeout)
        assertEquals("application/json", connection.getRequestProperty("Accept"))
        assertFalse(connection.doOutput)
        assertTrue(connection.disconnected)
    }

    @Test fun redirectsAndErrorsNeverReadAResponseBody() {
        listOf(204, 301, 302, 303, 307, 308, 400, 401, 403, 500).forEach { status ->
            val connection = Connection(status)
            assertNull("HTTP $status", AutomationReadiness.fetchReadinessText(connection))
            assertFalse(connection.bodyRequested)
            assertFalse(connection.instanceFollowRedirects)
            assertTrue(connection.disconnected)
        }
    }

    @Test fun characterLimitAcceptsBoundaryAndRejectsOversizeWithoutDrainingBody() {
        listOf(0, 1, 8192, 8193, 100000).forEach { size ->
            val body = object : ByteArrayInputStream("가".repeat(size).toByteArray(Charsets.UTF_8)) {
                var closed = false
                override fun close() { closed = true; super.close() }
            }
            val connection = Connection(body = body)
            val text = AutomationReadiness.fetchReadinessText(connection)
            if (size <= 8192) assertEquals("가".repeat(size), text) else assertNull(text)
            if (size == 100000) assertTrue(body.available() > 0)
            assertTrue(body.closed)
            assertTrue(connection.disconnected)
        }
    }

    @Test fun fragmentedUtf8ResponseIsReadUntilEof() {
        val value = "{\"status\":\"상태 확인\"}"
        val body = object : ByteArrayInputStream(value.toByteArray(Charsets.UTF_8)) {
            override fun read(buffer: ByteArray, offset: Int, length: Int): Int =
                super.read(buffer, offset, minOf(length, 1))
        }
        val connection = Connection(body = body)
        assertEquals(value, AutomationReadiness.fetchReadinessText(connection))
        assertTrue(connection.disconnected)
    }

    @Test fun responseAndReadFailuresDisconnectAndCloseOpenedBody() {
        val body = object : InputStream() {
            var closed = false
            override fun read(): Int = throw IOException("read unavailable")
            override fun close() { closed = true }
        }
        val readFailure = Connection(body = body)
        val statusFailure = Connection(statusFailure = true)
        listOf(readFailure, statusFailure).forEach { connection ->
            try {
                AutomationReadiness.fetchReadinessText(connection)
                fail("IOException required")
            } catch (_: IOException) {
                assertTrue(connection.disconnected)
            }
        }
        assertTrue(body.closed)
        assertFalse(statusFailure.bodyRequested)
    }
}
