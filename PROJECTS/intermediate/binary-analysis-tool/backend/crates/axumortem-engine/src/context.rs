// ©AngelaMos | 2026
// context.rs

use std::sync::Arc;

use memmap2::Mmap;

use crate::formats::FormatResult;
use crate::passes::disasm::DisassemblyResult;
use crate::passes::entropy::EntropyResult;
use crate::passes::imports::ImportResult;
use crate::passes::strings::StringResult;
use crate::passes::threat::ThreatResult;

pub enum BinarySource {
    Mapped(Mmap),
    Buffered(Arc<[u8]>),
}

impl AsRef<[u8]> for BinarySource {
    fn as_ref(&self) -> &[u8] {
        match self {
            Self::Mapped(mmap) => mmap,
            Self::Buffered(buf) => buf,
        }
    }
}

pub struct AnalysisContext {
    source: BinarySource,
    pub sha256: String,
    pub file_name: String,
    pub file_size: u64,
    pub format_result: Option<FormatResult>,
    pub import_result: Option<ImportResult>,
    pub string_result: Option<StringResult>,
    pub entropy_result: Option<EntropyResult>,
    pub disassembly_result: Option<DisassemblyResult>,
    pub threat_result: Option<ThreatResult>,
}

impl AnalysisContext {
    pub fn new(
        source: BinarySource,
        sha256: String,
        file_name: String,
        file_size: u64,
    ) -> Self {
        Self {
            source,
            sha256,
            file_name,
            file_size,
            format_result: None,
            import_result: None,
            string_result: None,
            entropy_result: None,
            disassembly_result: None,
            threat_result: None,
        }
    }

    pub fn data(&self) -> &[u8] {
        self.source.as_ref()
    }
}
